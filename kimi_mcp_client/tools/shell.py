from __future__ import annotations

import asyncio
import shlex

from ..sandbox.execpolicy import Action, PermissionEngine
from .spec import ToolResult


async def shell_tool(args: dict, permission_engine: PermissionEngine | None = None) -> ToolResult:
    command = args.get("command", "")
    timeout = int(args.get("timeout", 30))
    if permission_engine:
        verdict = permission_engine.evaluate("shell", None)
        if verdict == Action.DENY:
            return ToolResult(content="Denied by permission policy", is_error=True)
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        return ToolResult(content=f"Invalid command: {exc}", is_error=True)
    if not argv:
        return ToolResult(content="Empty command", is_error=True)
    proc = await asyncio.create_subprocess_exec(
        *argv,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except TimeoutError:
        proc.kill()
        return ToolResult(content="Command timed out", is_error=True)
    text = out.decode("utf-8", errors="ignore") + err.decode("utf-8", errors="ignore")
    return ToolResult(content=text.strip(), is_error=(proc.returncode != 0), metadata={"returncode": proc.returncode})
