---
name: python-async-mcp
description: Async Python MCP client with OpenAI integration, fiber-based tool execution, and streaming. Triggers - async tool execution, MCP servers, streaming LLM, fiber pattern.
version: 1.0.0
---

# Python Async MCP Client

## Overview

Build async Python clients for Model Context Protocol (MCP) servers with OpenAI-compatible APIs. Features fiber-based tool execution, streaming responses, and multi-turn conversations with automatic history management.

## File Structure

```
project/
├── kimi_full_client.py    # Main async client
├── pyproject.toml         # Package config
└── mcp_config.json        # MCP server definitions
```

## Implementation Pattern

### 1. Core Imports
```python
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from openai import AsyncOpenAI
import httpx

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
```

### 2. Fiber Executor (Tool Runner)
```python
class FiberExecutor:
    """Executes tools via MCP fiber API."""
    
    TOOL_MAP = {
        "web_search": "moonshot/web-search:latest",
        "fetch": "moonshot/fetch:latest",
        "code_runner": "moonshot/code_runner:latest",
    }
    PROTECTED = {"web_search", "search"}
    
    def __init__(self, api_key: str, base_url: str):
        self.http = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=90.0,
        )
        self._custom_fns: Dict[str, Callable[..., Any]] = {}
    
    def register(self, name: str, fn: Callable[..., Any]):
        """Register custom Python function as tool."""
        self._custom_fns[name] = fn
    
    async def execute(self, tool_call: Dict) -> str:
        """Execute a tool call via fiber API."""
        name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])
        
        # Check custom functions first
        if name in self._custom_fns:
            result = self._custom_fns[name](**args)
            return json.dumps(result) if not isinstance(result, str) else result
        
        # Execute via MCP fiber
        uri = self.TOOL_MAP.get(name)
        if not uri:
            return f"Unknown tool: {name}"
        
        resp = await self.http.post(
            f"/formulas/{uri}/fibers",
            json={"name": name, "arguments": json.dumps(args)},
        )
        fiber = resp.json()
        
        if fiber.get("status") == "succeeded":
            ctx = fiber.get("context", {})
            if name in self.PROTECTED and "encrypted_output" in ctx:
                return ctx["encrypted_output"]
            return ctx.get("output", str(ctx))
        
        return f"Error: {fiber.get('error', 'Unknown')}"
```

### 3. Session Manager
```python
class KimiSession:
    def __init__(
        self,
        model: str = "kimi-for-coding",
        system_prompt: str = "You are Kimi...",
        max_history: int = 40,
    ):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.executor = FiberExecutor(api_key, base_url)
        self.model = model
        self.max_history = max_history
        self.messages = [{"role": "system", "content": system_prompt}]
    
    async def chat(self, query: str, stream: bool = True) -> str:
        self.messages.append({"role": "user", "content": query})
        
        for _ in range(MAX_TOOL_ROUNDS):
            content, tool_calls = await self._stream_round()
            
            if not tool_calls:
                break
            
            # Execute tools concurrently
            results = await asyncio.gather(
                *(self.executor.execute(tc) for tc in tool_calls)
            )
            
            # Add results to history
            for tc, result in zip(tool_calls, results):
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": tc["function"]["name"],
                    "content": result,
                })
        
        return content
    
    async def _stream_round(self) -> tuple[str, list[dict]]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools,
            temperature=0.6,
            max_tokens=32768,
            stream=True,
            tool_choice="auto",
            extra_body={"thinking": {"type": "enabled"}},
        )
        
        content_parts = []
        tc_buf = {}
        
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
        
        return "".join(content_parts), list(tc_buf.values())
```

## Rules

### Do
- Use `async/await` for all I/O operations
- Register custom functions via `executor.register()`
- Handle protected tools (encrypted output) specially
- Set reasonable timeouts (90s for tools)
- Use `asyncio.gather()` for concurrent tool execution
- Trim history to prevent context overflow

### Don't
- Block the event loop with sync calls
- Expose API keys in code (use env vars)
- Forget to close httpx client (`aclose()`)
- Skip error handling for fiber API calls
- Store raw HTML/output in conversation history

## Tool Definition Format

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    }
]
```

## File Location
- `kimi_full_client.py` - Main implementation
- `kimi_thermo/` - Thermodynamic extensions

<!-- Generated by skill-master command
Version: 1.0.0
Sources:
- kimi_full_client.py
- kimi_thermo/thermo_executor.py
Last updated: 2026-03-20
-->
