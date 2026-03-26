"""Firecrawl MCP server — web scraping and data extraction via Firecrawl API."""

from __future__ import annotations

import os
from typing import Any

from .base import BaseMCPServer


class FirecrawlServer(BaseMCPServer):
    """Firecrawl for web scraping.

    Tools: scrape, crawl, extract, map, search
    """

    _BASE_URL = "https://api.firecrawl.dev/v1"
    _TOOLS = ["scrape", "crawl", "extract", "map", "search"]

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.api_key: str | None = (
            config.get("env", {}).get("FIRECRAWL_API_KEY")
            or os.environ.get("FIRECRAWL_API_KEY")
        )

    def _auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _require_key(self) -> None:
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY is not configured")

    async def health_check(self) -> dict[str, Any]:
        if not self.api_key:
            return {"status": "error", "error": "FIRECRAWL_API_KEY not set"}
        try:
            session = await self._get_session()
            async with session.post(
                f"{self._BASE_URL}/scrape",
                headers=self._auth_headers(),
                json={"url": "https://example.com", "formats": ["markdown"]},
            ) as resp:
                if resp.status in (200, 400):
                    # 400 means the key is valid but the URL/params were rejected
                    return {"status": "healthy", "api_key": f"{self.api_key[:8]}…", "tools": self._TOOLS}
                if resp.status == 401:
                    return {"status": "error", "error": "Invalid API key"}
                return {"status": "error", "error": f"HTTP {resp.status}"}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    async def scrape(
        self,
        url: str,
        formats: list[str] | None = None,
        only_main_content: bool = True,
        wait_for: int = 0,
    ) -> dict[str, Any]:
        """Scrape a single page."""
        self._require_key()
        self._track_request()
        payload: dict[str, Any] = {
            "url": url,
            "formats": formats or ["markdown"],
            "onlyMainContent": only_main_content,
        }
        if wait_for > 0:
            payload["waitFor"] = wait_for
        session = await self._get_session()
        async with session.post(f"{self._BASE_URL}/scrape", headers=self._auth_headers(), json=payload) as resp:
            if resp.status == 200:
                return await resp.json()
            raise RuntimeError(f"Firecrawl scrape failed: HTTP {resp.status} — {await resp.text()}")

    async def extract(
        self,
        urls: list[str],
        prompt: str,
        schema: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Extract structured data from a list of URLs."""
        self._require_key()
        self._track_request()
        payload: dict[str, Any] = {"urls": urls, "prompt": prompt}
        if schema:
            payload["schema"] = schema
        session = await self._get_session()
        async with session.post(f"{self._BASE_URL}/extract", headers=self._auth_headers(), json=payload) as resp:
            if resp.status == 200:
                return (await resp.json()).get("data", [])
            raise RuntimeError(f"Firecrawl extract failed: HTTP {resp.status} — {await resp.text()}")

    async def map(self, url: str, search: str | None = None, limit: int = 100) -> list[str]:
        """Discover URLs on a website."""
        self._require_key()
        self._track_request()
        params: dict[str, Any] = {"url": url, "limit": limit}
        if search:
            params["search"] = search
        session = await self._get_session()
        # Firecrawl /map uses POST, not GET
        async with session.post(f"{self._BASE_URL}/map", headers=self._auth_headers(), json=params) as resp:
            if resp.status == 200:
                return (await resp.json()).get("links", [])
            raise RuntimeError(f"Firecrawl map failed: HTTP {resp.status} — {await resp.text()}")

    async def crawl(
        self,
        url: str,
        limit: int = 10,
        max_depth: int = 2,
        formats: list[str] | None = None,
    ) -> dict[str, Any]:
        """Crawl multiple pages from a starting URL."""
        self._require_key()
        self._track_request()
        payload: dict[str, Any] = {
            "url": url,
            "limit": limit,
            "maxDepth": max_depth,
            "formats": formats or ["markdown"],
        }
        session = await self._get_session()
        async with session.post(f"{self._BASE_URL}/crawl", headers=self._auth_headers(), json=payload) as resp:
            if resp.status == 200:
                return await resp.json()
            raise RuntimeError(f"Firecrawl crawl failed: HTTP {resp.status} — {await resp.text()}")

    async def search(
        self,
        query: str,
        limit: int = 5,
        formats: list[str] | None = None,
    ) -> dict[str, Any]:
        """Search the web and extract content."""
        self._require_key()
        self._track_request()
        payload: dict[str, Any] = {"query": query, "limit": limit, "formats": formats or ["markdown"]}
        session = await self._get_session()
        async with session.post(f"{self._BASE_URL}/search", headers=self._auth_headers(), json=payload) as resp:
            if resp.status == 200:
                return await resp.json()
            raise RuntimeError(f"Firecrawl search failed: HTTP {resp.status} — {await resp.text()}")
