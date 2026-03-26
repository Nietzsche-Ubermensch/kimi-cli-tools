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
from .workflows import MCPWorkflows


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
        
        # Initialize all servers (idempotent — skip already-initialised ones)
        status = {}
        servers_config = self._config.get("mcpServers", {})
        for name, server_class in self._server_registry().items():
            try:
                if name not in self._servers:
                    self._servers[name] = server_class(servers_config.get(name, {}))
                    self.session.servers_used.append(name)
                status[name] = await self._servers[name].health_check()
            except Exception as e:
                status[name] = {"status": "error", "error": str(e)}
        
        # Print status summary
        healthy = sum(1 for s in status.values() if s.get("status") == "healthy")
        print(f"✅ Initialized {len(self._servers)} servers ({healthy} healthy)")
        
        for name, s in status.items():
            icon = "🟢" if s.get("status") == "healthy" else "🟡" if s.get("status") == "unconfigured" else "🔴"
            print(f"   {icon} {name}: {s.get('status', 'unknown')}")
        
        return status
    
    def _load_config(self) -> Dict:
        """Load MCP configuration from JSON file.

        Falls back to an empty config dict when the file is absent so that
        servers relying solely on environment variables still initialise.
        """
        if not os.path.exists(self.config_path):
            import warnings
            warnings.warn(
                f"Config file '{self.config_path}' not found. "
                "Servers will use environment variables only.",
                stacklevel=3
            )
            return {"mcpServers": {}}
        try:
            with open(self.config_path) as f:
                return json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in config file '{self.config_path}': {exc}"
            ) from exc
    
    def _server_registry(self) -> Dict[str, Any]:
        """Registry of all MCP servers."""
        return {
            "perplexity": PerplexityServer,
            "linear": LinearServer,
            "github": GitHubServer,
            "brave": BraveSearchServer,
            "firecrawl": FirecrawlServer,
            "chrome": ChromeDevToolsServer,
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
        return self._servers.get("brave")
    
    @property
    def firecrawl(self) -> FirecrawlServer:
        """Access Firecrawl server."""
        return self._servers.get("firecrawl")
    
    @property
    def chrome(self) -> ChromeDevToolsServer:
        """Access Chrome DevTools server."""
        return self._servers.get("chrome")
    
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
            # BUG-003 FIX: .seconds gives only the seconds component (0-59);
            # .total_seconds() gives the full elapsed duration.
            "duration_seconds": (datetime.now() - self.session.started_at).total_seconds(),
            "servers_used": self.session.servers_used,
            "actions_taken": self.session.actions_taken,
            "yolo_mode": self.session.yolo_mode
        }
    
    async def close(self):
        """Close all server connections."""
        for name, server in self._servers.items():
            try:
                await server.close()
            except Exception as e:
                print(f"Warning: Error closing {name}: {e}")


# Global client instance (singleton pattern)
_client_instance: Optional[KimiMCPClient] = None


def get_client(yolo_mode: bool = False, config_path: str = "mcp_config.json") -> KimiMCPClient:
    """Get or create global MCP client instance.

    A new instance is created whenever yolo_mode or config_path differs from
    the existing singleton so callers always get a client matching their
    requested configuration.
    """
    global _client_instance
    if (
        _client_instance is None
        or _client_instance.yolo_mode != yolo_mode
        or _client_instance.config_path != config_path
    ):
        _client_instance = KimiMCPClient(yolo_mode=yolo_mode, config_path=config_path)
    return _client_instance
