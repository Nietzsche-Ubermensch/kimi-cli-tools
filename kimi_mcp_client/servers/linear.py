"""
Linear MCP Server Implementation
Issue tracking and project management via Linear GraphQL API
"""

import os
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseMCPServer


class LinearServer(BaseMCPServer):
    """
    Linear for issue tracking and project management.
    
    Tools:
        - create_issue, update_issue, get_issue
        - search_issues, list_issues
        - create_comment, add_label
        - get_teams, get_projects, get_cycles
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("env", {}).get("LINEAR_API_KEY") or os.environ.get("LINEAR_API_KEY")
        self.graphql_url = "https://api.linear.app/graphql"
    
    async def _graphql_query(self, query: str, variables: Dict = None) -> Dict[str, Any]:
        """Execute a GraphQL query against Linear API."""
        if not self.api_key:
            raise ValueError("LINEAR_API_KEY not set")
        
        session = await self._get_session()
        async with session.post(
            self.graphql_url,
            headers={
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            },
            json={"query": query, "variables": variables or {}}
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                if "errors" in result:
                    raise Exception(f"Linear GraphQL error: {result['errors']}")
                return result.get("data", {})
            else:
                text = await resp.text()
                raise Exception(f"Linear API error: {resp.status} - {text}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Verify Linear API access."""
        if not self.api_key:
            return {"status": "error", "error": "LINEAR_API_KEY not set"}
        
        try:
            # Get current viewer to verify API access
            query = """
            query {
                viewer {
                    id
                    name
                    email
                }
                teams {
                    nodes {
                        id
                        name
                        key
                    }
                }
            }
            """
            result = await self._graphql_query(query)
            viewer = result.get("viewer", {})
            teams = result.get("teams", {}).get("nodes", [])
            
            return {
                "status": "healthy",
                "user": viewer.get("name"),
                "email": viewer.get("email"),
                "teams": [t.get("name") for t in teams],
                "api_key": f"{self.api_key[:8]}..."
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
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
        
        mutation = """
        mutation CreateIssue($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    description
                    priority
                    url
                    createdAt
                    team {
                        id
                        name
                    }
                }
            }
        }
        """
        
        input_data = {
            "title": title,
            "teamId": team_id,
            "description": description,
            "priority": priority
        }
        if labels:
            input_data["labelIds"] = labels
        
        result = await self._graphql_query(mutation, {"input": input_data})
        issue = result.get("issueCreate", {}).get("issue", {})
        
        return {
            "id": issue.get("id"),
            "identifier": issue.get("identifier"),
            "title": issue.get("title"),
            "description": issue.get("description"),
            "priority": issue.get("priority"),
            "teamId": team_id,
            "url": issue.get("url"),
            "created_at": issue.get("createdAt")
        }
    
    async def get_issues(self, team_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent issues.

        BUG-014 FIX: team_id was interpolated directly into the GraphQL
        query string (injection risk).  Use a typed GraphQL variable instead.
        """
        self._track_request()

        if team_id:
            query = """
            query GetIssues($first: Int!, $teamId: ID!) {
                issues(first: $first, filter: { team: { id: { eq: $teamId } } }) {
                    nodes {
                        id
                        identifier
                        title
                        description
                        priority
                        state {
                            name
                        }
                        url
                        createdAt
                    }
                }
            }
            """
            variables: Dict = {"first": limit, "teamId": team_id}
        else:
            query = """
            query GetIssues($first: Int!) {
                issues(first: $first) {
                    nodes {
                        id
                        identifier
                        title
                        description
                        priority
                        state {
                            name
                        }
                        url
                        createdAt
                    }
                }
            }
            """
            variables = {"first": limit}

        result = await self._graphql_query(query, variables)
        issues = result.get("issues", {}).get("nodes", [])
        
        return [{
            "id": i.get("id"),
            "identifier": i.get("identifier"),
            "title": i.get("title"),
            "description": i.get("description"),
            "priority": i.get("priority"),
            "state": i.get("state", {}).get("name"),
            "url": i.get("url"),
            "created_at": i.get("createdAt")
        } for i in issues]
    
    async def update_issue(
        self,
        issue_id: str,
        title: str = None,
        description: str = None,
        state: str = None
    ) -> Dict[str, Any]:
        """Update an existing issue."""
        self._track_request()
        
        mutation = """
        mutation UpdateIssue($input: IssueUpdateInput!) {
            issueUpdate(input: $input) {
                success
                issue {
                    id
                    title
                    description
                    state {
                        name
                    }
                }
            }
        }
        """
        
        input_data = {"id": issue_id}
        if title:
            input_data["title"] = title
        if description:
            input_data["description"] = description
        if state:
            input_data["stateId"] = state
        
        result = await self._graphql_query(mutation, {"input": input_data})
        issue = result.get("issueUpdate", {}).get("issue", {})
        
        return {
            "id": issue_id,
            "updated": True,
            "title": issue.get("title"),
            "description": issue.get("description"),
            "state": issue.get("state", {}).get("name")
        }
    
    async def get_teams(self) -> List[Dict[str, Any]]:
        """Get available teams."""
        self._track_request()
        
        query = """
        query {
            teams {
                nodes {
                    id
                    name
                    key
                    description
                }
            }
        }
        """
        
        result = await self._graphql_query(query)
        teams = result.get("teams", {}).get("nodes", [])
        
        return [{
            "id": t.get("id"),
            "name": t.get("name"),
            "key": t.get("key"),
            "description": t.get("description")
        } for t in teams]
    
    async def get_issue(self, issue_id: str) -> Dict[str, Any]:
        """Get a single issue by ID.

        BUG-015 FIX: issue_id was interpolated into the query string.
        """
        self._track_request()

        query = """
        query GetIssue($id: String!) {
            issue(id: $id) {
                id
                identifier
                title
                description
                priority
                state {
                    name
                }
                team {
                    id
                    name
                }
                url
                createdAt
            }
        }
        """

        result = await self._graphql_query(query, {"id": issue_id})
        issue = result.get("issue", {})
        
        return {
            "id": issue.get("id"),
            "identifier": issue.get("identifier"),
            "title": issue.get("title"),
            "description": issue.get("description"),
            "priority": issue.get("priority"),
            "state": issue.get("state", {}).get("name"),
            "team": issue.get("team", {}).get("name"),
            "url": issue.get("url"),
            "created_at": issue.get("createdAt")
        }
    
    async def search_issues(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for issues.

        BUG-015 FIX (continued): query string was interpolated directly.
        """
        self._track_request()

        graphql_query = """
        query SearchIssues($query: String!, $first: Int!) {
            issueSearch(query: $query, first: $first) {
                nodes {
                    id
                    identifier
                    title
                    description
                    priority
                    state {
                        name
                    }
                    url
                }
            }
        }
        """

        result = await self._graphql_query(graphql_query, {"query": query, "first": limit})
        issues = result.get("issueSearch", {}).get("nodes", [])
        
        return [{
            "id": i.get("id"),
            "identifier": i.get("identifier"),
            "title": i.get("title"),
            "description": i.get("description"),
            "priority": i.get("priority"),
            "state": i.get("state", {}).get("name"),
            "url": i.get("url")
        } for i in issues]
