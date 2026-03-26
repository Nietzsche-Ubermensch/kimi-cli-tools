"""Brave Search MCP server — privacy-focused web search via Brave Search API."""

from __future__ import annotations

import os
from typing import Any

from .base import BaseMCPServer


class BraveSearchServer(BaseMCPServer):
    """Brave Search for web discovery.

    Tools: web_search, image_search, video_search, news_search
    """

    _BASE_URL = "https://api.search.brave.com/res/v1"
    _TOOLS = ["web_search", "image_search", "video_search", "news_search"]

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.api_key: str | None = (
            config.get("env", {}).get("BRAVE_API_KEY")
            or os.environ.get("BRAVE_API_KEY")
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key or "",
        }

    def _require_key(self) -> None:
        if not self.api_key:
            raise ValueError("BRAVE_API_KEY is not configured")

    async def health_check(self) -> dict[str, Any]:
        if not self.api_key:
            return {"status": "error", "error": "BRAVE_API_KEY not set"}
        try:
            session = await self._get_session()
            async with session.get(
                f"{self._BASE_URL}/web/search",
                headers=self._headers(),
                params={"q": "test", "count": 1},
            ) as resp:
                if resp.status == 200:
                    return {"status": "healthy", "api_key": f"{self.api_key[:8]}…", "tools": self._TOOLS}
                return {"status": "error", "error": f"HTTP {resp.status}"}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    async def web_search(
        self,
        query: str,
        count: int = 10,
        offset: int = 0,
        freshness: str | None = None,
    ) -> dict[str, Any]:
        """Search the web. freshness: pd/pw/pm/py for recency filtering."""
        self._require_key()
        self._track_request()
        params: dict[str, Any] = {"q": query, "count": min(max(count, 1), 20), "offset": offset}
        if freshness:
            params["freshness"] = freshness
        session = await self._get_session()
        async with session.get(f"{self._BASE_URL}/web/search", headers=self._headers(), params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            raise RuntimeError(f"Brave web search failed: HTTP {resp.status} — {await resp.text()}")

    async def image_search(self, query: str, count: int = 50) -> list[dict[str, Any]]:
        """Search for images."""
        self._require_key()
        self._track_request()
        session = await self._get_session()
        async with session.get(f"{self._BASE_URL}/images/search", headers=self._headers(), params={"q": query, "count": min(count, 100)}) as resp:
            if resp.status == 200:
                return (await resp.json()).get("results", [])
            raise RuntimeError(f"Brave image search failed: HTTP {resp.status} — {await resp.text()}")

    async def news_search(self, query: str, count: int = 20, freshness: str = "pd") -> list[dict[str, Any]]:
        """Search recent news articles."""
        self._require_key()
        self._track_request()
        session = await self._get_session()
        async with session.get(f"{self._BASE_URL}/news/search", headers=self._headers(), params={"q": query, "count": min(count, 50), "freshness": freshness}) as resp:
            if resp.status == 200:
                return (await resp.json()).get("results", [])
            raise RuntimeError(f"Brave news search failed: HTTP {resp.status} — {await resp.text()}")

    async def video_search(self, query: str, count: int = 20) -> list[dict[str, Any]]:
        """Search for videos."""
        self._require_key()
        self._track_request()
        session = await self._get_session()
        async with session.get(f"{self._BASE_URL}/videos/search", headers=self._headers(), params={"q": query, "count": min(count, 50)}) as resp:
            if resp.status == 200:
                return (await resp.json()).get("results", [])
            raise RuntimeError(f"Brave video search failed: HTTP {resp.status} — {await resp.text()}")
