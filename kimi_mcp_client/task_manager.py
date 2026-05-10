from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable


@dataclass
class TaskRecord:
    id: str
    state: str = "queued"
    timeline: list[dict[str, Any]] = field(default_factory=list)
    artifact_refs: list[str] = field(default_factory=list)
    checklist: dict[str, bool] = field(default_factory=dict)
    schema_version: int = 1


class DurableTaskManager:
    def __init__(self, max_workers: int = 2, base_dir: Path | None = None):
        self.max_workers = max_workers
        self.base_dir = base_dir or (Path.home() / ".kimi" / "tasks")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.queue: asyncio.Queue = asyncio.Queue()
        self.workers: list[asyncio.Task] = []
        self.handlers: dict[str, Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]] = {}

    def _file(self, task_id: str) -> Path:
        return self.base_dir / f"{task_id}.json"

    def register_handler(self, name: str, handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]) -> None:
        self.handlers[name] = handler

    def _save(self, rec: TaskRecord) -> None:
        self._file(rec.id).write_text(json.dumps(rec.__dict__, indent=2), encoding="utf-8")

    def create_task(self, kind: str, payload: dict[str, Any]) -> TaskRecord:
        rec = TaskRecord(id=str(uuid.uuid4()))
        rec.timeline.append({"event": "created", "kind": kind})
        self._save(rec)
        self.queue.put_nowait((rec.id, kind, payload))
        return rec

    def get_task(self, task_id: str) -> dict[str, Any]:
        return json.loads(self._file(task_id).read_text(encoding="utf-8"))

    def cancel_task(self, task_id: str) -> None:
        rec = TaskRecord(**self.get_task(task_id))
        rec.state = "canceled"
        rec.timeline.append({"event": "canceled"})
        self._save(rec)

    async def _worker(self) -> None:
        while True:
            task_id, kind, payload = await self.queue.get()
            rec = TaskRecord(**self.get_task(task_id))
            if rec.state == "canceled":
                self.queue.task_done()
                continue
            rec.state = "running"
            rec.timeline.append({"event": "running"})
            self._save(rec)
            try:
                if kind not in self.handlers:
                    raise KeyError(f"No handler registered for task kind: {kind}")
                handler = self.handlers[kind]
                result = await handler(payload)
                rec.state = "completed"
                rec.timeline.append({"event": "completed", "result": result})
            except Exception as exc:
                rec.state = "failed"
                rec.timeline.append({"event": "failed", "error": str(exc)})
            self._save(rec)
            self.queue.task_done()

    async def start(self) -> None:
        if not self.workers:
            self.workers = [asyncio.create_task(self._worker()) for _ in range(self.max_workers)]

    async def stop(self) -> None:
        for worker in self.workers:
            worker.cancel()
        self.workers.clear()
