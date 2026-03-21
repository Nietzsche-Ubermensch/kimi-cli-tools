#!/usr/bin/env python3
"""Kimi Full Client — async streaming with fiber tool execution."""

import asyncio
import json
import base64
import os
import sys
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from openai import AsyncOpenAI
import httpx

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

log = logging.getLogger(__name__)
MAX_TOOL_ROUNDS = 10


def _load_config() -> tuple[str, str]:
    config_path = Path.home() / ".kimi" / "config.toml"
    key = os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")
    url = os.getenv("KIMI_BASE_URL") or os.getenv("MOONSHOT_BASE_URL", "https://api.kimi.com/coding/v1")
    if not key and config_path.exists():
        with open(config_path, "rb") as f:
            cfg = tomllib.load(f)
        for prov in cfg.get("providers", {}).values():
            if prov.get("api_key"):
                key = prov["api_key"]
                url = prov.get("base_url", url)
                break
    if not key:
        print("Error: Set KIMI_API_KEY or configure ~/.kimi/config.toml", file=sys.stderr)
        sys.exit(1)
    return key, url

API_KEY, BASE_URL = _load_config()

class FiberExecutor:

    TOOL_MAP = {
        "web_search":       "moonshot/web-search:latest",
        "search":           "moonshot/web-search:latest",
        "crawl":            "moonshot/crawl:latest",
        "fetch":            "moonshot/fetch:latest",
        "date":             "moonshot/date:latest",
        "convert":          "moonshot/convert:latest",
        "quickjs":          "moonshot/quickjs:latest",
        "random_choice":    "moonshot/random-choice:latest",
        "memory":           "moonshot/memory:latest",
        "code_runner":      "moonshot/code_runner:latest",
        "base64_encode":    "moonshot/base64:latest",
        "base64_decode":    "moonshot/base64:latest",
        "base64":           "moonshot/base64:latest",
        "excel":            "moonshot/excel:latest",
        "mew_generator":    "moonshot/mew:latest",
        "mew":              "moonshot/mew:latest",
        "rethink":          "moonshot/rethink:latest",
        "calculate_length": "moonshot/calculate_length:latest",
    }
    PROTECTED = {"web_search", "search"}

    def __init__(self, api_key: str):
        self.http = httpx.AsyncClient(
            base_url=BASE_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=90.0,
        )
        self._custom_fns: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]):
        self._custom_fns[name] = fn

    async def execute(self, tool_call: Dict) -> str:
        name = tool_call["function"]["name"]
        try:
            args = json.loads(tool_call["function"]["arguments"])
        except json.JSONDecodeError as e:
            return f"Error: malformed arguments — {e}"

        if name in self._custom_fns:
            try:
                result = self._custom_fns[name](**args)
                return json.dumps(result) if not isinstance(result, str) else result
            except Exception as e:
                return json.dumps({"error": str(e)})

        uri = self.TOOL_MAP.get(name)
        if not uri:
            return f"Unknown tool: {name}"

        try:
            resp = await self.http.post(
                f"/formulas/{uri}/fibers",
                json={"name": name, "arguments": json.dumps(args)},
            )
            resp.raise_for_status()
            fiber = resp.json()

            if fiber.get("status") == "succeeded":
                ctx = fiber.get("context", {})
                if name in self.PROTECTED and "encrypted_output" in ctx:
                    return ctx["encrypted_output"]
                return ctx.get("output", str(ctx))

            err = (fiber.get("error")
                   or fiber.get("context", {}).get("error", "Unknown error"))
            return f"Error: {err}"

        except httpx.HTTPStatusError as e:
            return f"HTTP {e.response.status_code}: {e.response.text[:200]}"
        except Exception as e:
            log.exception("Tool %s failed", name)
            return f"Execution failed: {e}"

    async def aclose(self):
        await self.http.aclose()

TOOLS: List[Dict] = [
    {"type": "function", "function": {"name": "web_search", "description": "Search the web for information", "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "What to search for"}, "classes": {"type": "array", "items": {"type": "string", "enum": ["all", "academic", "social", "library", "finance", "code", "ecommerce", "medical"]}, "description": "Search domains"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "crawl", "description": "Fetch and clean URL content as Markdown", "parameters": {"type": "object", "properties": {"url": {"type": "string", "description": "URL to crawl"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "fetch", "description": "URL content extraction", "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "max_length": {"type": "integer", "default": 5000}, "raw": {"type": "boolean", "default": False}, "start_index": {"type": "integer", "default": 0}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "code_runner", "description": "Execute Python code safely", "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}}},
    {"type": "function", "function": {"name": "quickjs", "description": "Execute JavaScript code safely", "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}}},
    {"type": "function", "function": {"name": "convert", "description": "Unit conversion (length, mass, currency, temp, etc.)", "parameters": {"type": "object", "properties": {"value": {"type": "number"}, "from_unit": {"type": "string"}, "to_unit": {"type": "string"}}, "required": ["value", "from_unit", "to_unit"]}}},
    {"type": "function", "function": {"name": "date", "description": "Date/time processing and timezone conversion", "parameters": {"type": "object", "properties": {"operation": {"type": "string", "enum": ["time", "convert", "between", "add", "subtract"]}, "date": {"type": "string"}, "date1": {"type": "string"}, "date2": {"type": "string"}, "days": {"type": "integer"}, "format": {"type": "string", "default": "%Y-%m-%d %H:%M:%S"}, "zone": {"type": "string"}, "from_zone": {"type": "string"}, "to_zone": {"type": "string"}}, "required": ["operation"]}}},
    {"type": "function", "function": {"name": "base64_encode", "description": "Encode text to base64", "parameters": {"type": "object", "properties": {"data": {"type": "string"}, "encoding": {"type": "string", "default": "utf-8"}}, "required": ["data"]}}},
    {"type": "function", "function": {"name": "base64_decode", "description": "Decode base64 text", "parameters": {"type": "object", "properties": {"data": {"type": "string"}, "encoding": {"type": "string", "default": "utf-8"}}, "required": ["data"]}}},
    {"type": "function", "function": {"name": "excel", "description": "Excel/CSV analysis", "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}}},
    {"type": "function", "function": {"name": "memory", "description": "Store/retrieve persistent data (TTL 24h default)", "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["store", "retrieve", "delete", "list"]}, "key": {"type": "string"}, "data": {"type": "object"}, "prefix": {"type": "string"}, "ttl": {"type": "integer", "default": 86400}}, "required": ["action"]}}},
    {"type": "function", "function": {"name": "random_choice", "description": "Weighted random selection", "parameters": {"type": "object", "properties": {"candidates": {"type": "array", "items": {"type": "string"}}, "count": {"type": "integer", "default": 1}, "replace": {"type": "boolean", "default": False}, "weights": {"type": "array", "items": {"type": "number"}}, "seed": {"type": "integer"}, "format": {"type": "string", "enum": ["simple", "detailed", "json"], "default": "simple"}}, "required": ["candidates"]}}},
    {"type": "function", "function": {"name": "rethink", "description": "Organize thoughts and plan next steps", "parameters": {"type": "object", "properties": {"thought": {"type": "string"}}, "required": ["thought"]}}},
    {"type": "function", "function": {"name": "calculate_length", "description": "Calculate text or token length", "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "mode": {"type": "string", "enum": ["chars", "tokens"]}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "mew_generator", "description": "Random cat meow with blessing", "parameters": {"type": "object", "properties": {"mood": {"type": "string", "enum": ["happy", "sleepy", "hungry", "playful", "grumpy"]}}}}},
]

def encode_image(path: str) -> str:
    ext = Path(path).suffix.lower().lstrip(".")
    mime = {"png": "image/png", "gif": "image/gif", "webp": "image/webp"}.get(
        ext, "image/jpeg"
    )
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"


class KimiSession:

    def __init__(
        self,
        model: str = "kimi-for-coding",
        system_prompt: str = "You are Kimi, an AI assistant by Moonshot AI. "
                             "Use tools when needed. Respond in the user's language.",
        max_history: int = 40,
        tools: Optional[List[Dict]] = None,
    ):
        self.client = AsyncOpenAI(
            api_key=API_KEY, base_url=BASE_URL,
            default_headers={"User-Agent": "kimi-cli/1.22.0"},
        )
        self.executor = FiberExecutor(API_KEY)
        self.model = model
        self.max_history = max_history
        self.tools = list(tools or TOOLS)
        self.messages: List[Dict] = [{"role": "system", "content": system_prompt}]

    def _trim_history(self):
        while len(self.messages) > self.max_history * 2 + 1:
            self.messages.pop(1)
            if len(self.messages) > 1:
                self.messages.pop(1)

    def clear(self):
        self.messages = [self.messages[0]]

    def get_history(self) -> List[Dict]:
        return self.messages.copy()

    def add_tool(self, schema: Dict, fn: Callable[..., Any]):
        self.tools.append(schema)
        self.executor.register(schema["function"]["name"], fn)

    async def chat(
        self,
        query: str,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        file_path: Optional[str] = None,
        stream: bool = True,
    ) -> str:
        user_content: list = [{"type": "text", "text": query}]
        if image_url:
            user_content.append({"type": "image_url", "image_url": {"url": image_url}})
        elif image_path:
            user_content.append({"type": "image_url", "image_url": {"url": encode_image(image_path)}})
        if video_url:
            user_content.append({"type": "video_url", "video_url": {"url": video_url}})
        if file_path:
            user_content.append({"type": "file", "file": {"path": file_path}})

        self.messages.append({"role": "user", "content": user_content})
        content = ""

        for _round in range(MAX_TOOL_ROUNDS):
            if stream:
                content, tool_calls = await self._stream_round()
            else:
                content, tool_calls = await self._sync_round()

            assistant_msg: Dict = {"role": "assistant", "content": content}
            if tool_calls:
                assistant_msg["tool_calls"] = tool_calls
            self.messages.append(assistant_msg)

            if not tool_calls:
                break

            results = await asyncio.gather(
                *(self.executor.execute(tc) for tc in tool_calls)
            )
            for tc, result in zip(tool_calls, results):
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": tc["function"]["name"],
                    "content": result,
                })
        else:
            log.warning("Hit max tool rounds (%d)", MAX_TOOL_ROUNDS)

        self._trim_history()
        return content

    async def _stream_round(self) -> tuple[str, list[dict]]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools,
            temperature=0.6,
            max_tokens=32768,
            top_p=0.95,
            stream=True,
            tool_choice="auto",
            extra_body={"thinking": {"type": "enabled"}},
        )

        content_parts: list[str] = []
        tc_buf: dict[int, dict] = {}

        print("Kimi: ", end="", flush=True)
        async for chunk in response:
            delta = chunk.choices[0].delta

            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                print(delta.reasoning_content, end="", flush=True)

            if delta.content:
                content_parts.append(delta.content)
                print(delta.content, end="", flush=True)

            if delta.tool_calls:
                for tcd in delta.tool_calls:
                    idx = tcd.index
                    if idx not in tc_buf:
                        tc_buf[idx] = {
                            "id": tcd.id,
                            "type": "function",
                            "function": {"name": "", "arguments": ""},
                        }
                    entry = tc_buf[idx]
                    if tcd.function.name:
                        entry["function"]["name"] = tcd.function.name
                    if tcd.function.arguments:
                        entry["function"]["arguments"] += tcd.function.arguments
        print()

        return "".join(content_parts), list(tc_buf.values())

    async def _sync_round(self) -> tuple[str, list[dict]]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools,
            temperature=0.6,
            max_tokens=32768,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        content = msg.content or ""
        tool_calls = []
        if msg.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]
            print(f"Kimi: {content}" if content else "", end="")
            for tc in tool_calls:
                print(f"\n  -> {tc['function']['name']}()", end="")
            print()
        else:
            print(f"Kimi: {content}")

        return content, tool_calls

    async def aclose(self):
        await self.executor.aclose()


async def repl():
    session = KimiSession()
    print("Kimi CLI | /clear /history /quit")
    print()

    try:
        while True:
            try:
                query = input("You: ").strip()
            except EOFError:
                break

            if not query:
                continue
            if query in ("/quit", "/exit", "/q"):
                break
            if query == "/clear":
                session.clear()
                print("(history cleared)")
                continue
            if query == "/history":
                for i, m in enumerate(session.get_history()):
                    role = m["role"]
                    preview = str(m.get("content", ""))[:80]
                    print(f"  [{i}] {role}: {preview}")
                continue

            await session.chat(query)
            print()
    finally:
        await session.aclose()


async def main():
    if len(sys.argv) > 1 and sys.argv[1] not in ("-i", "--interactive"):
        session = KimiSession()
        query = " ".join(sys.argv[1:])
        await session.chat(query)
        await session.aclose()
    else:
        await repl()


def _cli_entry():
    asyncio.run(main())

if __name__ == "__main__":
    _cli_entry()
