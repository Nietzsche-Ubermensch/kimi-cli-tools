"""
Kimi MCP Client - Full Implementation
8-server MCP orchestration with real tool execution
"""

__version__ = "1.0.0"
__author__ = "Nietzsche-Ubermensch"

from .client import KimiMCPClient
from .workflows import MCPWorkflows
from .servers import (
    PerplexityServer,
    LinearServer,
    GitHubServer,
    BraveSearchServer,
    FirecrawlServer,
    ChromeDevToolsServer,
    PlaywrightServer,
    Context7Server,
)

__all__ = [
    "KimiMCPClient",
    "MCPWorkflows",
    "PerplexityServer",
    "LinearServer",
    "GitHubServer",
    "BraveSearchServer",
    "FirecrawlServer",
    "ChromeDevToolsServer",
    "PlaywrightServer",
    "Context7Server",
]
