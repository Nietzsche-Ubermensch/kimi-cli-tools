from __future__ import annotations

import asyncio
import json
from typing import Any


class JsonRpcLspClient:
    def __init__(self, command: list[str]):
        self.command = command
        self.proc: asyncio.subprocess.Process | None = None
        self._id = 0
        self._reader_task: asyncio.Task | None = None

    async def start(self) -> bool:
        self.proc = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        self._reader_task = asyncio.create_task(self._drain_stdout())
        return True

    async def _drain_stdout(self) -> None:
        if not self.proc or not self.proc.stdout:
            return
        while True:
            line = await self.proc.stdout.readline()
            if not line:
                break

    async def request(self, method: str, params: dict[str, Any]) -> None:
        if not self.proc or not self.proc.stdin:
            return
        self._id += 1
        payload = json.dumps({"jsonrpc": "2.0", "id": self._id, "method": method, "params": params})
        frame = f"Content-Length: {len(payload)}\r\n\r\n{payload}".encode("utf-8")
        self.proc.stdin.write(frame)
        await self.proc.stdin.drain()

    async def stop(self) -> None:
        if self._reader_task:
            self._reader_task.cancel()
            self._reader_task = None
        if self.proc and self.proc.returncode is None:
            self.proc.terminate()
            await self.proc.wait()
