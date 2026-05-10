from __future__ import annotations

import argparse
import asyncio
import os

from .client import OpenAICompatibleClient
from .config import load_config
from .core.engine import AgentEngine
from .runtime_api import serve_http
from .tui.ui import run_tui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kimi",
        description="Kimi CLI (DeepSeek-inspired architecture, Kimi runtime semantics)",
    )
    parser.add_argument("--one-shot", dest="one_shot")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--model")
    parser.add_argument("--yolo", action="store_true")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--config", default="config.toml")
    sub = parser.add_subparsers(dest="command")
    serve = sub.add_parser("serve")
    serve.add_argument("--http", action="store_true")
    return parser


async def _run(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    settings = cfg.settings
    settings.yolo = bool(args.yolo)
    settings.plan_mode = bool(args.plan)
    if args.model:
        settings.model = args.model

    llm = OpenAICompatibleClient(settings.base_url, os.environ.get("KIMI_API_KEY") or os.environ.get("MOONSHOT_API_KEY"))
    engine = AgentEngine(settings=settings, llm_client=llm, config=cfg)

    # Non-TUI mode: no interactive terminal bootstrap.
    if args.command == "serve" and args.http:
        await serve_http(engine, cfg.raw.get("runtime_api", {}))
        return 0

    if args.one_shot:
        response = await engine.handle_prompt(args.one_shot)
        print(response)
        await llm.close()
        return 0

    # TUI mode branch: terminal UI lifecycle ownership begins here.
    await run_tui(engine)
    await llm.close()
    return 0


def main() -> int:
    return asyncio.run(_run(build_parser().parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
