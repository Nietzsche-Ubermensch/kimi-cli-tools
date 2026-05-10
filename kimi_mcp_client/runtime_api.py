from __future__ import annotations

import asyncio
import json
from aiohttp import web

from .task_manager import DurableTaskManager


def create_app(engine, task_manager: DurableTaskManager | None = None) -> web.Application:
    app = web.Application()
    tm = task_manager or DurableTaskManager(max_workers=engine.settings.max_workers)
    token = engine.config.raw.get("runtime_api", {}).get("token")

    async def _ensure_auth(request: web.Request) -> web.Response | None:
        if not token:
            return None
        if request.headers.get("Authorization") != f"Bearer {token}":
            return web.json_response({"error": "unauthorized"}, status=401)
        return None

    async def handle_turn_task(payload: dict) -> dict:
        content = await engine.handle_prompt(payload.get("prompt", ""))
        return {"content": content}

    async def create_thread(request: web.Request) -> web.Response:
        unauthorized = await _ensure_auth(request)
        if unauthorized:
            return unauthorized
        thread = engine.threads.create_thread()
        return web.json_response(thread, status=201)

    async def thread_events(request: web.Request) -> web.StreamResponse:
        unauthorized = await _ensure_auth(request)
        if unauthorized:
            return unauthorized
        thread_id = request.match_info["thread_id"]
        since_seq = int(request.query.get("since_seq", "0"))
        data = engine.threads.get_thread(thread_id)
        resp = web.StreamResponse(status=200, headers={"Content-Type": "text/event-stream"})
        await resp.prepare(request)
        for seq, event in enumerate(data.get("events", [])[since_seq:], start=since_seq):
            payload = json.dumps({"seq": seq, "event": event})
            await resp.write(f"data: {payload}\n\n".encode("utf-8"))
        await resp.write_eof()
        return resp

    async def start_turn(request: web.Request) -> web.Response:
        unauthorized = await _ensure_auth(request)
        if unauthorized:
            return unauthorized
        body = await request.json()
        content = await engine.handle_prompt(body.get("prompt", ""))
        return web.json_response({"content": content}, status=201)

    async def create_task(request: web.Request) -> web.Response:
        unauthorized = await _ensure_auth(request)
        if unauthorized:
            return unauthorized
        body = await request.json()
        rec = tm.create_task(body.get("kind", "turn"), body.get("payload", {}))
        return web.json_response(rec.__dict__, status=201)

    async def get_task(request: web.Request) -> web.Response:
        unauthorized = await _ensure_auth(request)
        if unauthorized:
            return unauthorized
        return web.json_response(tm.get_task(request.match_info["task_id"]))

    async def delete_task(request: web.Request) -> web.Response:
        unauthorized = await _ensure_auth(request)
        if unauthorized:
            return unauthorized
        tm.cancel_task(request.match_info["task_id"])
        return web.Response(status=204)

    app.add_routes(
        [
            web.post("/v1/threads", create_thread),
            web.get("/v1/threads/{thread_id}/events", thread_events),
            web.post("/v1/threads/{thread_id}/turns", start_turn),
            web.post("/v1/tasks", create_task),
            web.get("/v1/tasks/{task_id}", get_task),
            web.delete("/v1/tasks/{task_id}", delete_task),
        ]
    )

    async def on_startup(_: web.Application) -> None:
        tm.register_handler("turn", handle_turn_task)
        await tm.start()

    async def on_cleanup(_: web.Application) -> None:
        await tm.stop()

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app


async def serve_http(engine, cfg: dict | None = None, stop_event: asyncio.Event | None = None) -> None:
    cfg = cfg or {}
    app = create_app(engine)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, cfg.get("host", "127.0.0.1"), int(cfg.get("port", 8765)))
    await site.start()
    if stop_event is None:
        stop_event = asyncio.Event()
    await stop_event.wait()
