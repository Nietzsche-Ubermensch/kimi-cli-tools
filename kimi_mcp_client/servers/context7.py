"""Context7 MCP server — library documentation lookup via Upstash/Context7 API."""

from __future__ import annotations

import os
from typing import Any

from .base import BaseMCPServer


class Context7Server(BaseMCPServer):
    """Context7 for library documentation lookup.

    Tools: resolve_library, query_docs, list_libraries
    """

    _BASE_URL = "https://api.upstash.com/context7/v1"
    _TOOLS = ["resolve_library", "query_docs", "list_libraries"]

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.api_key: str | None = (
            config.get("env", {}).get("CONTEXT7_API_KEY")
            or os.environ.get("CONTEXT7_API_KEY")
        )

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    def _require_key(self) -> None:
        if not self.api_key:
            raise ValueError("CONTEXT7_API_KEY is not configured")

    async def health_check(self) -> dict[str, Any]:
        if not self.api_key:
            return {
                "status": "unconfigured",
                "error": "CONTEXT7_API_KEY not set",
                "setup_url": "https://upstash.com/",
                "tools": self._TOOLS,
            }
        try:
            session = await self._get_session()
            async with session.get(
                f"{self._BASE_URL}/libraries",
                headers=self._auth_headers(),
                params={"limit": 1},
            ) as resp:
                if resp.status == 200:
                    return {"status": "healthy", "api_key": f"{self.api_key[:8]}…", "tools": self._TOOLS}
                return {"status": "error", "error": f"HTTP {resp.status}"}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    async def resolve_library(self, library_name: str, query: str | None = None) -> dict[str, Any]:
        """Find library documentation by name."""
        self._require_key()
        self._track_request()
        session = await self._get_session()
        async with session.get(
            f"{self._BASE_URL}/libraries",
            headers=self._auth_headers(),
            params={"query": library_name},
        ) as resp:
            if resp.status == 200:
                libraries: list[dict[str, Any]] = (await resp.json()).get("libraries", [])
                return {
                    "library": library_name,
                    "query": query,
                    "matches": libraries[:5],
                    "best_match": libraries[0] if libraries else None,
                }
            raise RuntimeError(f"Context7 resolve failed: HTTP {resp.status} — {await resp.text()}")

    async def query_docs(self, library_id: str, query: str) -> dict[str, Any]:
        """Query documentation for a specific question."""
        self._require_key()
        self._track_request()
        # Normalise library_id: ensure it starts with "/"
        if not library_id.startswith("/"):
            library_id = f"/{library_id}"
        session = await self._get_session()
        async with session.post(
            f"{self._BASE_URL}{library_id}/query",
            headers={**self._auth_headers(), "Content-Type": "application/json"},
            json={"query": query},
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                return {
                    "library_id": library_id,
                    "query": query,
                    "answer": result.get("answer", ""),
                    "code_examples": result.get("code_examples", []),
                    "sources": result.get("sources", []),
                }
            raise RuntimeError(f"Context7 query failed: HTTP {resp.status} — {await resp.text()}")

    async def list_libraries(self, limit: int = 50) -> list[dict[str, Any]]:
        """List available library documentations."""
        self._require_key()
        self._track_request()
        session = await self._get_session()
        async with session.get(
            f"{self._BASE_URL}/libraries",
            headers=self._auth_headers(),
            params={"limit": limit},
        ) as resp:
            if resp.status == 200:
                return (await resp.json()).get("libraries", [])
            raise RuntimeError(f"Context7 list_libraries failed: HTTP {resp.status} — {await resp.text()}")
