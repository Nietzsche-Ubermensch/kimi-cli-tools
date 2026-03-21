"""
Base Server Class for MCP Implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseMCPServer(ABC):
    """Base class for all MCP server implementations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__.replace("Server", "").lower()
        self.last_used: Optional[datetime] = None
        self.request_count = 0
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check server health and return status."""
        pass
    
    def _track_request(self):
        """Track request metrics."""
        self.last_used = datetime.now()
        self.request_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server usage statistics."""
        return {
            "name": self.name,
            "requests": self.request_count,
            "last_used": self.last_used.isoformat() if self.last_used else None
        }
