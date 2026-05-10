from __future__ import annotations

import asyncio

from prompt_toolkit import PromptSession
from rich.console import Console
from rich.panel import Panel

from .app import AppState


async def run_tui(engine) -> None:
    console = Console()
    state = AppState()
    prompt = PromptSession("kimi> ")

    async def event_listener() -> None:
        while True:
            event = await engine.events.get()
            state.on_event(event)
            if event.type == "tool_called":
                console.print(Panel(f"Tool: {event.tool_name}"))
            if event.type == "turn_complete":
                console.print(Panel(event.content, title="Assistant"))

    listener = asyncio.create_task(event_listener())
    try:
        while True:
            text = await prompt.prompt_async()
            if text.strip() in {"/exit", "exit", "quit"}:
                break
            await engine.handle_prompt(text)
    finally:
        listener.cancel()
        try:
            await listener
        except asyncio.CancelledError:
            pass
