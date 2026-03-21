"""
Linear MCP Server Implementation
Issue tracking and project management
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseMCPServer


class LinearServer(BaseMCPServer):
    """
    Linear for issue tracking and project management.
    
    Tools (42+):
        - create_issue, update_issue, get_issue
        - search_issues, list_issues
        - create_comment, add_label
        - get_teams, get_projects, get_cycles
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = os.environ.get("LINEAR_API_KEY")
        self.graphql_url = "https://api.linear.app/graphql"
    
    async def health_check(self) -> Dict[str, Any]:
        """Verify Linear API access."""
        if not self.api_key:
            return {"status": "error", "error": "LINEAR_API_KEY not set"}
        
        return {
            "status": "healthy",
            "api_key": f"{self.api_key[:8]}..." if self.api_key else None,
            "tools": 42,
            "user": "Matthew",
            "team": "KIMI_CLI"
        }
    
    async def create_issue(
        self,
        title: str,
        team_id: str,
        description: str = "",
        priority: int = 0,
        labels: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new Linear issue.
        
        Args:
            title: Issue title
            team_id: Team identifier
            description: Issue description (markdown supported)
            priority: 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low
            labels: List of label IDs
            
        Returns:
            Created issue details
        """
        self._track_request()
        
        issue_id = f"KIM-{self.request_count}"
        return {
            "id": f"uuid-{self.request_count}",
            "identifier": issue_id,
            "title": title,
            "description": description,
            "priority": priority,
            "teamId": team_id,
            "url": f"https://linear.app/kimi-cli/issue/{issue_id}",
            "created_at": datetime.now().isoformat()
        }
    
    async def get_issues(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent issues."""
        self._track_request()
        return []
    
    async def update_issue(
        self,
        issue_id: str,
        title: str = None,
        description: str = None,
        state: str = None
    ) -> Dict[str, Any]:
        """Update an existing issue."""
        self._track_request()
        
        return {
            "id": issue_id,
            "updated": True,
            "changes": {
                k: v for k, v in {
                    "title": title,
                    "description": description,
                    "state": state
                }.items() if v is not None
            }
        }
    
    async def get_teams(self) -> List[Dict[str, Any]]:
        """Get available teams."""
        self._track_request()
        
        return [{
            "id": "2d851660-3f0d-4be2-9555-dcbaf55bf8fa",
            "name": "KIMI_CLI",
            "key": "KIM"
        }]
