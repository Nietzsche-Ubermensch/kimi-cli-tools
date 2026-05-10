from __future__ import annotations

import json
from typing import Awaitable, Callable

from ..models import ChatMessage, LLMRequest
from ..tools.registry import ToolRegistry
from .turn import Turn


async def run_streaming_turn(
    turn: Turn,
    *,
    model: str,
    llm_client,
    messages: list[ChatMessage],
    registry: ToolRegistry,
    on_tool_call: Callable[[str, dict], Awaitable[None]] | None = None,
) -> str:
    request = LLMRequest(model=model, messages=messages, stream=True)
    text_chunks: list[str] = []

    async for chunk in llm_client.stream(request):
        if chunk.text:
            text_chunks.append(chunk.text)

    combined = "\n".join(text_chunks).strip()
    if not combined:
        turn.response = ""
        return ""

    # Minimal DeepSeek-style tool block: {"tool":"name","args":{...}}
    try:
        if not combined.startswith("{"):
            raise json.JSONDecodeError("not-json", combined, 0)
        payload = json.loads(combined)
        if isinstance(payload, dict) and payload.get("tool"):
            tool_name = payload["tool"]
            args = payload.get("args", {})
            if on_tool_call:
                await on_tool_call(tool_name, args)
            result = await registry.dispatch(tool_name, args)
            turn.tool_results.append({"tool": tool_name, "result": result.content})
            turn.response = result.content
            return result.content
    except json.JSONDecodeError:
        pass

    turn.response = combined
    return combined
