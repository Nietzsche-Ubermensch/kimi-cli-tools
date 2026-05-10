# Kimi CLI Architecture (DeepSeek TUI-aligned)

This repository now follows a 5-layer architecture:

1. **User Interface Layer**
   - `kimi_mcp_client/main.py`: argparse entrypoint, one-shot/serve/resume/yolo/plan routing.
   - `kimi_mcp_client/tui/`: rich + prompt_toolkit app state, streaming, approval, clipboard.

2. **Core Engine Layer**
   - `kimi_mcp_client/core/engine.py`: async agent loop, checkpointing, event bus.
   - `kimi_mcp_client/core/turn_loop.py`: streaming turn execution and tool dispatch loop.
   - `kimi_mcp_client/core/capacity_flow.py`: soft/hard token guardrails.
   - `kimi_mcp_client/core/events.py`, `session.py`, `turn.py`, `ops.py`: typed runtime models.

3. **Tool & Extension Layer**
   - `kimi_mcp_client/tools/`: registry/spec + shell/file/todo/tasks/github/plan/subagent/rlm/automation tools.
   - `kimi_mcp_client/hooks/lifecycle.py`: pre/post tool hook execution.
   - `kimi_mcp_client/skills/loader.py`: SKILL.md discovery across home/workspace paths.
   - `kimi_mcp_client/mcp/client.py`: wiring for existing 8 MCP servers.

4. **Runtime API + Task Management**
   - `kimi_mcp_client/runtime_api.py`: aiohttp HTTP/SSE runtime API.
   - `kimi_mcp_client/task_manager.py`: durable queue, worker pool, timelines.
   - `kimi_mcp_client/runtime_threads.py`: thread/turn/event persistence.

5. **LLM Layer**
   - `kimi_mcp_client/llm_client.py`: abstract client + retry.
   - `kimi_mcp_client/client.py`: async Kimi/OpenAI-compatible HTTP streaming client.
   - `kimi_mcp_client/models.py`: typed pydantic request/response models.

## LSP Integration

- `kimi_mcp_client/lsp/manager.py` performs lazy startup per file extension.
- Missing binaries degrade silently.
- Tool registry invokes LSP post-edit hook after `write_file`, `edit_file`, and `apply_patch`.
- Engine injects pending diagnostics into the next model turn.

## Runtime Durability

- Turn checkpoint: `~/.kimi/sessions/checkpoints/latest.json`
- Offline queue: `~/.kimi/sessions/checkpoints/offline_queue.json`
- Tasks: `~/.kimi/tasks/*.json`
- Threads: `~/.kimi/threads/*.json`

## Modes

- **Normal**: approvals/hooks/policies apply.
- **Plan mode**: edit tools blocked via registry guard.
- **YOLO mode**: no approval UI guard, optimized for autonomous runs.
- **One-shot**: single turn and exit via `--one-shot`.

## Layer-by-layer module ownership reference (Kimi Python runtime)

This is the Python equivalent of DeepSeek TUI ownership boundaries. The architecture is inspired by DeepSeek, but runtime identity and command semantics remain Kimi-first.

### `kimi_mcp_client/main.py` — process entry + mode selection + TUI ownership boundary

- Owns mode routing: `serve --http`, `--one-shot`, and interactive TUI.
- Must keep non-TUI commands free from interactive terminal bootstrap.
- Must keep TUI startup/shutdown orchestration centralized (do not move ownership into core/tool layers).

### `kimi_mcp_client/tui/app.py` — top-level TUI app state

- Owns UI state transitions and event-to-state mapping.
- Must bubble shutdown/interrupt/cancellation outcomes to the caller (`main.py`/`tui.ui` flow).
- Must not manipulate global terminal mode directly.

### `kimi_mcp_client/tui/ui.py` — render/event loop

- Owns prompt/render loop mechanics and clean loop shutdown.
- Must not bypass upstream cleanup path.
- Global mode transitions should remain in bootstrap owner paths, not deep render handlers.

### `kimi_mcp_client/tui/approval.py`, `streaming.py`, `clipboard.py` — specialized UI helpers

- Terminal-mode agnostic helper modules.
- Must not install competing global panic/error hooks.
- Fatal paths should surface errors to central loop/teardown.

### `kimi_mcp_client/core/*` — engine/turn/state transport

- Terminal responsibility: none.
- Must remain runtime-behavior focused and reusable from both TUI and runtime API.
- Must expose cancellation and error semantics that UI and API can map cleanly.

### `kimi_mcp_client/tools/*` — tool execution layer

- Must run equivalently in TUI and runtime API contexts.
- Must not perform terminal mode manipulation.
- Interactive approval needs must route through abstractions/events, not direct terminal reads in tool handlers.

### `kimi_mcp_client/hooks/lifecycle.py` — hook dispatch

- Must emit failures as regular runtime errors/events.
- Hook failures must not bypass cleanup paths in upper layers.

### `kimi_mcp_client/mcp/client.py` — MCP integration

- Transport/server failures propagate as tool/runtime errors.
- Must remain terminal-state independent.

### `kimi_mcp_client/runtime_api.py` — HTTP/SSE runtime API

- Must be fully operable without TTY.
- Must not initialize interactive terminal mode.
