"""Playwright MCP server stub.

Full Playwright browser automation requires the external MCP server:
    npx -y @executeautomation/playwright-mcp-server

This stub surfaces correct health-check status and delegates all actual
automation to either the real Playwright MCP server (if configured) or
the Firecrawl server for content extraction.
"""

from __future__ import annotations

from typing import Any

from .base import BaseMCPServer

_SETUP_CMD = "npx -y @executeautomation/playwright-mcp-server"
_TOOLS = ["new_page", "goto", "click", "fill", "screenshot", "get_by_role", "expect"]
_NOTE = f"Full automation requires the Playwright MCP server: {_SETUP_CMD}"


class PlaywrightServer(BaseMCPServer):
    """Playwright for cross-browser automation (stub — see module docstring)."""

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.browsers = ["chromium", "firefox", "webkit"]

    async def health_check(self) -> dict[str, Any]:
        return {
            "status": "unconfigured",
            "message": _NOTE,
            "browsers": self.browsers,
            "tools": _TOOLS,
        }

    async def new_page(self, browser: str = "chromium", headless: bool = True) -> dict[str, Any]:
        self._track_request()
        return {"page_id": f"page_{self.request_count}", "browser": browser, "headless": headless, "note": _NOTE}

    async def goto(self, page_id: str, url: str, wait_until: str = "networkidle") -> dict[str, Any]:
        self._track_request()
        return {"page_id": page_id, "url": url, "note": "Use firecrawl.scrape for content extraction."}

    async def click(self, page_id: str, selector: str) -> dict[str, Any]:
        self._track_request()
        return {"clicked": False, "selector": selector, "note": _NOTE}

    async def fill(self, page_id: str, selector: str, value: str) -> dict[str, Any]:
        self._track_request()
        return {"filled": False, "selector": selector, "note": _NOTE}

    async def screenshot(self, page_id: str, path: str | None = None, full_page: bool = False) -> dict[str, Any]:
        self._track_request()
        return {"page_id": page_id, "path": path, "full_page": full_page, "note": "Use firecrawl.scrape with screenshot format."}

    async def get_by_role(self, page_id: str, role: str, name: str | None = None) -> dict[str, Any]:
        self._track_request()
        return {"role": role, "name": name, "found": False, "note": _NOTE}

    async def expect(self, page_id: str, selector: str, condition: str, timeout: int = 5000) -> dict[str, Any]:
        self._track_request()
        return {"pass": False, "condition": condition, "note": _NOTE}
