from __future__ import annotations

import json

from .spec import ToolResult


def build_task_tools(task_manager):
    async def task_create(args: dict) -> ToolResult:
        rec = task_manager.create_task(args.get("kind", "turn"), args.get("payload", {}))
        return ToolResult(content=rec.id)

    async def task_update(args: dict) -> ToolResult:
        task_id = args["id"]
        rec = task_manager.get_task(task_id)
        rec.setdefault("checklist", {}).update(args.get("checklist", {}))
        task_manager._file(task_id).write_text(json.dumps(rec, indent=2), encoding="utf-8")
        return ToolResult(content="task updated")

    async def task_gate_run(args: dict) -> ToolResult:
        return ToolResult(content="gate passed" if args.get("approved", False) else "gate blocked", is_error=not args.get("approved", False))

    async def task_shell_wait(args: dict) -> ToolResult:
        return ToolResult(content=f"waited for task {args.get('id', '')}")

    async def pr_attempt(args: dict) -> ToolResult:
        return ToolResult(content=f"pr attempt for task {args.get('id', '')}")

    return {
        "task_create": task_create,
        "task_update": task_update,
        "task_gate_run": task_gate_run,
        "task_shell_wait": task_shell_wait,
        "pr_attempt": pr_attempt,
    }
