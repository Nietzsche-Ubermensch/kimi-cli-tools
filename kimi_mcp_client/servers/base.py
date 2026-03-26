"""Base class for all MCP server implementations."""

from __future__ import annotations

import aiohttp
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

# Default timeouts (seconds). Override per-server via config["timeout"].
_DEFAULT_CONNECT_TIMEOUT = 5.0
_DEFAULT_READ_TIMEOUT = 30.0


class BaseMCPServer(ABC):
    """Base class for all MCP server implementations."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        # Derive a clean name: "BraveSearchServer" → "bravesearch"
        self.name: str = self.__class__.__name__.lower().removesuffix("server")
        self.last_used: datetime | None = None
        self.request_count: int = 0
        self._session: aiohttp.ClientSession | None = None

        # Per-server timeout from config; fall back to module defaults
        raw = config.get("timeout")
        total = float(raw) if isinstance(raw, (int, float)) and raw > 0 else _DEFAULT_READ_TIMEOUT
        self.timeout = aiohttp.ClientTimeout(
            connect=_DEFAULT_CONNECT_TIMEOUT,
            total=total,
        )

    # ── Session management ────────────────────────────────────────────────

    async def _get_session(self) -> aiohttp.ClientSession:
        """Return the shared session, creating it lazily when needed."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def close(self) -> None:
        """Close the shared HTTP session and release the reference."""
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    # ── Subclass contract ─────────────────────────────────────────────────

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check server health and return a status dict."""

    # ── Metrics ───────────────────────────────────────────────────────────

    def _track_request(self) -> None:
        """Record that one request was dispatched."""
        self.last_used = datetime.now(tz=timezone.utc)
        self.request_count += 1

    def get_stats(self) -> dict[str, Any]:
        """Return server usage statistics."""
        return {
            "name": self.name,
            "requests": self.request_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }
