from __future__ import annotations

import aiohttp
import json
from typing import AsyncIterator, Optional

from .llm_client import AbstractLLMClient, with_retry
from .mcp.client import MCPClient
from .models import LLMChunk, LLMRequest


class OpenAICompatibleClient(AbstractLLMClient):
    """Async Kimi/OpenAI-compatible client with SSE/chunk support."""

    def __init__(self, base_url: str, api_key: str | None, timeout_sec: int = 60):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout_sec)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def stream(self, request: LLMRequest) -> AsyncIterator[LLMChunk]:
        if not self.api_key:
            yield LLMChunk(text="[offline] missing API key", done=True)
            return

        async def _do_request() -> list[LLMChunk]:
            session = await self._get_session()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = request.model_dump()
            chunks: list[LLMChunk] = []
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()
                async for raw_line in response.content:
                    line = raw_line.decode("utf-8", errors="ignore").strip()
                    if not line:
                        continue
                    if line.startswith("data: "):
                        line = line[6:]
                    if line == "[DONE]":
                        chunks.append(LLMChunk(done=True, raw={"done": True}))
                        break
                    token = line
                    try:
                        payload_json = json.loads(line)
                        choices = payload_json.get("choices", [])
                        if choices:
                            token = choices[0].get("delta", {}).get("content", "") or token
                        chunks.append(LLMChunk(text=token, raw=payload_json))
                    except json.JSONDecodeError:
                        chunks.append(LLMChunk(text=token, raw={"line": line}))
            return chunks

        for chunk in await with_retry(_do_request):
            yield chunk

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()


class KimiMCPClient(MCPClient):
    """Backward-compatible MCP orchestration client alias."""


def get_client(config_path: str = "mcp_config.json") -> KimiMCPClient:
    return KimiMCPClient(config_path=config_path)
