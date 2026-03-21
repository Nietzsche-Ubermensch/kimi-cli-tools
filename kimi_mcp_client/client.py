#!/usr/bin/env python3
"""
Kimi MCP Client - Main Client Implementation
Orchestrates all 8 MCP servers with real tool execution
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from .servers import *


@dataclass
class MCPSession:
    """Tracks MCP session state and history."""
    started_at: datetime
    servers_used: List[str]
    actions_taken: int
    yolo_mode: bool


class KimiMCPClient:
    """
    Main MCP client that orchestrates all 8 servers.
    
    Usage:
        client = KimiMCPClient(yolo_mode=True)
        await client.initialize()
        
        # Execute workflows
        result = await client.workflows.research_to_linear("React 19", team_id)
    """
    
    def __init__(self, yolo_mode: bool = False, config_path: str = "mcp_config.json"):
        self.yolo_mode = yolo_mode
        self.config_path = config_path
        self.session = MCPSession(
            started_at=datetime.now(),
            servers_used=[],
            actions_taken=0,
            yolo_mode=yolo_mode
        )
        
        # Server instances (initialized on demand)
        self._servers: Dict[str, Any] = {}
        self._config: Optional[Dict] = None
        
        # Workflow handler
        self.workflows = MCPWorkflows(self)
    
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize the MCP client and verify all servers.
        
        Returns:
            Status report of all servers
        """
        print("🚀 Initializing Kimi MCP Client...")
        print(f"   Yolo Mode: {'ON' if self.yolo_mode else 'OFF'}")
        print(f"   Config: {self.config_path}")
        
        # Load configuration
        self._config = self._load_config()
        
        # Initialize all servers
        status = {}
        for name, server_class in self._server_registry().items():
            try:
                server = server_class(self._config.get("mcpServers", {}).get(name, {}))
                self._servers[name] = server
                status[name] = await server.health_check()
                self.session.servers_used.append(name)
            except Exception as e:
                status[name] = {"status": "error", "error": str(e)}
        
        print(f"✅ Initialized {len(self._servers)} servers")
        return status
    
    def _load_config(self) -> Dict:
        """Load MCP configuration from JSON file."""
        with open(self.config_path) as f:
            return json.load(f)
    
    def _server_registry(self) -> Dict[str, Any]:
        """Registry of all MCP servers."""
        return {
            "perplexity": PerplexityServer,
            "linear": LinearServer,
            "github": GitHubServer,
            "brave-search": BraveSearchServer,
            "firecrawl": FirecrawlServer,
            "chrome-devtools": ChromeDevToolsServer,
            "playwright": PlaywrightServer,
            "context7": Context7Server,
        }
    
    # Direct server accessors
    @property
    def perplexity(self) -> PerplexityServer:
        """Access Perplexity server."""
        return self._servers.get("perplexity")
    
    @property
    def linear(self) -> LinearServer:
        """Access Linear server."""
        return self._servers.get("linear")
    
    @property
    def github(self) -> GitHubServer:
        """Access GitHub server."""
        return self._servers.get("github")
    
    @property
    def brave(self) -> BraveSearchServer:
        """Access Brave Search server."""
        return self._servers.get("brave-search")
    
    @property
    def firecrawl(self) -> FirecrawlServer:
        """Access Firecrawl server."""
        return self._servers.get("firecrawl")
    
    @property
    def chrome(self) -> ChromeDevToolsServer:
        """Access Chrome DevTools server."""
        return self._servers.get("chrome-devtools")
    
    @property
    def playwright(self) -> PlaywrightServer:
        """Access Playwright server."""
        return self._servers.get("playwright")
    
    @property
    def context7(self) -> Context7Server:
        """Access Context7 server."""
        return self._servers.get("context7")
    
    async def execute_chain(self, steps: List[Callable]) -> List[Any]:
        """
        Execute a chain of operations across multiple servers.
        
        Args:
            steps: List of async functions to execute in sequence
            
        Returns:
            List of results from each step
        """
        results = []
        for step in steps:
            result = await step()
            results.append(result)
            self.session.actions_taken += 1
        return results
    
    def get_session_report(self) -> Dict[str, Any]:
        """Get current session statistics."""
        return {
            "started_at": self.session.started_at.isoformat(),
            "duration_seconds": (datetime.now() - self.session.started_at).seconds,
            "servers_used": self.session.servers_used,
            "actions_taken": self.session.actions_taken,
            "yolo_mode": self.session.yolo_mode
        }


# Global client instance (singleton pattern)
_client_instance: Optional[KimiMCPClient] = None


def get_client(yolo_mode: bool = False) -> KimiMCPClient:
    """Get or create global MCP client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = KimiMCPClient(yolo_mode=yolo_mode)
    return _client_instance
