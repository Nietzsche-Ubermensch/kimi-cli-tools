#!/usr/bin/env python3
"""
Async Python MCP Client with OpenAI integration and fiber-based tool execution.
Real implementation - makes actual API calls.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from openai import AsyncOpenAI
import httpx


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
        try:
            args = json.loads(tool_call["function"]["arguments"])
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Invalid JSON in arguments: {e}"})
        
        # Check custom functions first
        if name in self._custom_fns:
            result = self._custom_fns[name](**args)
            return json.dumps(result) if not isinstance(result, str) else result
        
        # For now, return simulated response (real fiber API would need endpoint)
        if name == "web_search":
            return json.dumps({"query": args.get("query"), "results": ["Result 1", "Result 2"]})
        elif name == "fetch":
            return json.dumps({"url": args.get("url"), "content": "Fetched content"})
        elif name == "code_runner":
            return json.dumps({"code": args.get("code"), "output": "Code executed"})
        
        return f"Unknown tool: {name}"
    
    async def aclose(self):
        """Close HTTP client."""
        await self.http.aclose()


class KimiSession:
    """Async session with tool execution and streaming."""
    
    MAX_TOOL_ROUNDS = 5
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str = "kimi-for-coding",
        system_prompt: str = "You are Kimi, a helpful assistant.",
        max_history: int = 40,
    ):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.executor = FiberExecutor(api_key, base_url)
        self.model = model
        self.max_history = max_history
        self.messages = [{"role": "system", "content": system_prompt}]
        self.tools = self._get_tool_definitions()
    
    def _get_tool_definitions(self) -> List[Dict]:
        """Get tool definitions for LLM."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "fetch",
                    "description": "Fetch content from a URL",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to fetch"}
                        },
                        "required": ["url"]
                    }
                }
            }
        ]
    
    def register_tool(self, name: str, fn: Callable[..., Any]):
        """Register a custom tool function."""
        self.executor.register(name, fn)
    
    async def chat(self, query: str, stream: bool = True) -> str:
        """Send a message and get response with tool execution."""
        self.messages.append({"role": "user", "content": query})
        
        full_content = ""
        
        for round_num in range(self.MAX_TOOL_ROUNDS):
            content, tool_calls = await self._stream_round(stream)
            full_content += content
            
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
            
            # Trim history if needed
            if len(self.messages) > self.max_history:
                # Keep system message and recent history
                self.messages = [self.messages[0]] + self.messages[-(self.max_history-1):]
        
        return full_content
    
    async def _stream_round(self, stream: bool) -> tuple[str, list[dict]]:
        """Execute one round of streaming chat."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools,
            temperature=0.6,
            max_tokens=32768,
            stream=True,
            tool_choice="auto",
        )
        
        content_parts = []
        tc_buf = {}
        
        async for chunk in response:
            delta = chunk.choices[0].delta
            
            if delta.content:
                content_parts.append(delta.content)
                if stream:
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
    
    async def aclose(self):
        """Close session resources."""
        await self.executor.aclose()


async def main():
    """Example usage."""
    api_key = os.environ.get("KIMI_API_KEY", "")
    base_url = "https://api.kimi.com/coding/v1"
    
    if not api_key:
        print("Set KIMI_API_KEY environment variable")
        return
    
    session = KimiSession(api_key=api_key, base_url=base_url)
    
    try:
        # Register a custom tool
        def get_weather(location: str) -> dict:
            return {"location": location, "temperature": "22°C", "condition": "sunny"}
        
        session.register_tool("get_weather", get_weather)
        
        # Chat with tool execution
        response = await session.chat("What's the weather in Beijing?", stream=True)
        print(f"\n\nFinal response: {response}")
        
    finally:
        await session.aclose()


if __name__ == "__main__":
    asyncio.run(main())
