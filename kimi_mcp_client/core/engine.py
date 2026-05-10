from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass
from pathlib import Path

from ..compaction import compact_messages
from ..models import ChatMessage
from ..runtime_threads import RuntimeThreadStore
from ..session import SerializableSession
from ..tools import build_default_registry
from ..tools.registry import ToolRegistry
from ..tools.plan import build_plan_tools
from ..tools.spec import ToolSpec
from ..lsp.manager import LspManager
from ..hooks.lifecycle import HookRunner
from .capacity_flow import CapacityGuardrails
from .events import ErrorEvent, ToolCalled, ToolResult, TurnComplete, TurnStarted
from .session import SessionState
from .turn import Turn
from .turn_loop import run_streaming_turn


@dataclass(slots=True)
class EngineConfig:
    checkpoint_path: Path
    offline_queue_path: Path


class AgentEngine:
    def __init__(self, *, settings, llm_client, config):
        self.settings = settings
        self.llm_client = llm_client
        self.config = config
        self.events: asyncio.Queue = asyncio.Queue()
        self.session = SessionState(session_id=str(uuid.uuid4()), plan_mode=settings.plan_mode)
        self.guardrails = CapacityGuardrails()
        self.lsp_manager = LspManager(enabled=settings.lsp_enabled)
        self.hooks = HookRunner(config.hooks)
        self.registry: ToolRegistry = build_default_registry(self.hooks, self.lsp_manager)
        for name, handler in build_plan_tools(self).items():
            self.registry.register(
                ToolSpec(
                    name=name,
                    description="Plan mode tool",
                    input_schema={"type": "object", "properties": {}},
                ),
                handler,
            )
        self.threads = RuntimeThreadStore()
        home = Path.home() / ".kimi" / "sessions" / "checkpoints"
        self.engine_config = EngineConfig(
            checkpoint_path=home / "latest.json",
            offline_queue_path=home / "offline_queue.json",
        )

    async def _emit(self, event) -> None:
        await self.events.put(event)

    def _checkpoint(self, prompt: str) -> None:
        self.engine_config.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine_config.checkpoint_path.write_text(
            json.dumps({"session_id": self.session.session_id, "prompt": prompt}),
            encoding="utf-8",
        )

    def _clear_checkpoint(self) -> None:
        if self.engine_config.checkpoint_path.exists():
            self.engine_config.checkpoint_path.unlink()

    async def _on_tool_call(self, name: str, args: dict) -> None:
        await self._emit(ToolCalled(type="tool_called", tool_name=name, args=args))

    def _save_session_snapshot(self) -> None:
        SerializableSession(
            session_id=self.session.session_id,
            data={"turns": [t.__dict__ for t in self.session.turns]},
        ).save(Path.home() / ".kimi" / "sessions" / "latest.json")

    async def handle_prompt(self, prompt: str) -> str:
        self._checkpoint(prompt)
        turn = Turn(turn_id=str(uuid.uuid4()), prompt=prompt)
        self.session.turns.append(turn)
        await self._emit(TurnStarted(type="turn_started", turn_id=turn.turn_id))

        messages = [ChatMessage(role="user", content=prompt)]
        if self.session.pending_diagnostics:
            messages.append(ChatMessage(role="user", content="LSP Diagnostics:\n" + "\n".join(self.session.pending_diagnostics)))
            self.session.pending_diagnostics.clear()

        messages = compact_messages(messages)

        try:
            content = await run_streaming_turn(
                turn,
                model=self.settings.model,
                llm_client=self.llm_client,
                messages=messages,
                registry=self.registry,
                on_tool_call=self._on_tool_call,
            )
            for item in turn.tool_results:
                await self._emit(ToolResult(type="tool_result", tool_name=item["tool"], result=item["result"]))
            await self._emit(TurnComplete(type="turn_complete", turn_id=turn.turn_id, content=content))
            self.threads.append_turn(self.session.session_id, turn)
            self._save_session_snapshot()
            self._clear_checkpoint()
            self.session.pending_diagnostics.extend(self.lsp_manager.pop_pending_messages())
            return content
        except Exception as exc:
            await self._emit(ErrorEvent(type="error", message=str(exc)))
            self._queue_offline(prompt)
            raise

    def _queue_offline(self, prompt: str) -> None:
        self.engine_config.offline_queue_path.parent.mkdir(parents=True, exist_ok=True)
        if self.engine_config.offline_queue_path.exists():
            items = json.loads(self.engine_config.offline_queue_path.read_text(encoding="utf-8"))
        else:
            items = []
        items.append({"session_id": self.session.session_id, "prompt": prompt})
        self.engine_config.offline_queue_path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    def set_plan_mode(self, enabled: bool) -> None:
        self.session.plan_mode = enabled
        self.registry.plan_mode = enabled
