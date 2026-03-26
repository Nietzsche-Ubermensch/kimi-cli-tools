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

# LaborMarket and SubAgent
from .soul.agent import LaborMarket, SubAgent

# Tools
from .tools.file_operations import FileManagerTool, Approval, Config, Runtime
from .tools.code_analyzer import (
    CodeAnalyzerTool,
    AnalyzerApproval,
    AnalyzerConfig,
    AnalyzerRuntime,
)

# Agents
from .agents.research_agent import ResearchOrchestrator

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
    # New components
    "LaborMarket",
    "SubAgent",
    "FileManagerTool",
    "CodeAnalyzerTool",
    "AnalyzerApproval",
    "AnalyzerConfig",
    "AnalyzerRuntime",
    "ResearchOrchestrator",
]
