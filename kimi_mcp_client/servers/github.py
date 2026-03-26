"""
GitHub MCP Server Implementation
Code management and repository operations via GitHub API
"""

import os
import aiohttp
import base64
from typing import Dict, Any, List, Optional
from .base import BaseMCPServer


class GitHubServer(BaseMCPServer):
    """
    GitHub for code operations.
    
    Tools:
        - search_code, get_file_contents
        - create_pull_request, merge_pull_request
        - create_issue, list_issues
        - create_or_update_file
        - fork_repository
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.token = config.get("env", {}).get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
        self.api_url = "https://api.github.com"
    
    def _headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "KimiMCPClient/1.0"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers
    
    async def health_check(self) -> Dict[str, Any]:
        """Verify GitHub API access."""
        if not self.token:
            return {"status": "error", "error": "GITHUB_TOKEN not set"}
        
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.api_url}/user",
                headers=self._headers()
            ) as resp:
                if resp.status == 200:
                    user = await resp.json()
                    return {
                        "status": "healthy",
                        "user": user.get("login"),
                        "token": f"{self.token[:8]}..."
                    }
                return {"status": "error", "error": f"API returned {resp.status}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def search_code(
        self,
        query: str,
        sort: str = "indexed",
        order: str = "desc",
        per_page: int = 10
    ) -> Dict[str, Any]:
        """
        Search code across GitHub.
        
        Args:
            query: Search query (supports GitHub search syntax)
            sort: indexed/best-match
            order: asc/desc
            per_page: Results per page
            
        Returns:
            Code search results
        """
        self._track_request()
        
        session = await self._get_session()
        async with session.get(
            f"{self.api_url}/search/code",
            headers=self._headers(),
            params={
                "q": query,
                "sort": sort,
                "order": order,
                "per_page": per_page
            }
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                text = await resp.text()
                raise Exception(f"GitHub search failed: {resp.status} - {text}")
    
    async def get_file_contents(
        self,
        owner: str,
        repo: str,
        path: str,
        branch: Optional[str] = None  # BUG-017 FIX: was `str = None` (missing Optional)
    ) -> Dict[str, Any]:
        """
        Get contents of a file or directory.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File or directory path
            branch: Branch name (defaults to default branch)
            
        Returns:
            File contents or directory listing
        """
        self._track_request()
        
        params = {}
        if branch:
            params["ref"] = branch
        
        session = await self._get_session()
        async with session.get(
            f"{self.api_url}/repos/{owner}/{repo}/contents/{path}",
            headers=self._headers(),
            params=params
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                text = await resp.text()
                raise Exception(f"GitHub get contents failed: {resp.status} - {text}")
    
    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: str = "",
        draft: bool = False
    ) -> Dict[str, Any]:
        """
        Create a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: PR title
            head: Branch with changes
            base: Branch to merge into
            body: PR description
            draft: Create as draft
            
        Returns:
            Created PR details
        """
        self._track_request()
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN not set")
        
        session = await self._get_session()
        async with session.post(
            f"{self.api_url}/repos/{owner}/{repo}/pulls",
            headers=self._headers(),
            json={
                "title": title,
                "head": head,
                "base": base,
                "body": body,
                "draft": draft
            }
        ) as resp:
            if resp.status == 201:
                return await resp.json()
            else:
                text = await resp.text()
                raise Exception(f"GitHub create PR failed: {resp.status} - {text}")
    
    async def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
        sha: Optional[str] = None  # BUG-017 FIX: was `str = None`
    ) -> Dict[str, Any]:
        """
        Create or update a file in a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            content: File content
            message: Commit message
            branch: Target branch
            sha: Required for updates (file SHA)
            
        Returns:
            Commit details
        """
        self._track_request()
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN not set")
        
        # Encode content to base64
        encoded_content = base64.b64encode(content.encode()).decode()
        
        payload = {
            "message": message,
            "content": encoded_content,
            "branch": branch
        }
        if sha:
            payload["sha"] = sha
        
        session = await self._get_session()
        async with session.put(
            f"{self.api_url}/repos/{owner}/{repo}/contents/{path}",
            headers=self._headers(),
            json=payload
        ) as resp:
            if resp.status in [200, 201]:
                return await resp.json()
            else:
                text = await resp.text()
                raise Exception(f"GitHub create/update file failed: {resp.status} - {text}")
    
    async def push_files(
        self,
        owner: str,
        repo: str,
        branch: str,
        files: List[Dict[str, str]],
        message: str
    ) -> Dict[str, Any]:
        """
        Push multiple files in a single commit.
        Note: GitHub API requires individual file commits, so this creates them sequentially.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Target branch
            files: List of {path, content} dicts
            message: Commit message
            
        Returns:
            Last commit details
        """
        self._track_request()
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN not set")
        
        last_result = None
        for file_info in files:
            result = await self.create_or_update_file(
                owner=owner,
                repo=repo,
                path=file_info["path"],
                content=file_info["content"],
                message=f"{message} - {file_info['path']}",
                branch=branch
            )
            last_result = result
        
        return {
            "commit": last_result.get("commit", {}) if last_result else {},
            "files_changed": len(files)
        }
    
    async def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        per_page: int = 30
    ) -> List[Dict[str, Any]]:
        """
        List issues in a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: open/closed/all
            per_page: Results per page
            
        Returns:
            List of issues
        """
        self._track_request()
        
        session = await self._get_session()
        async with session.get(
            f"{self.api_url}/repos/{owner}/{repo}/issues",
            headers=self._headers(),
            params={"state": state, "per_page": per_page}
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                text = await resp.text()
                raise Exception(f"GitHub list issues failed: {resp.status} - {text}")
    
    async def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str = "",
        labels: Optional[List[str]] = None  # BUG-017 FIX: mutable default None, not []
    ) -> Dict[str, Any]:
        """
        Create an issue in a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            body: Issue body
            labels: List of label names
            
        Returns:
            Created issue details
        """
        self._track_request()
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN not set")
        
        payload = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels
        
        session = await self._get_session()
        async with session.post(
            f"{self.api_url}/repos/{owner}/{repo}/issues",
            headers=self._headers(),
            json=payload
        ) as resp:
            if resp.status == 201:
                return await resp.json()
            else:
                text = await resp.text()
                raise Exception(f"GitHub create issue failed: {resp.status} - {text}")
    
    async def fork_repository(
        self,
        owner: str,
        repo: str,
        organization: Optional[str] = None  # BUG-017 FIX: was `str = None`
    ) -> Dict[str, Any]:
        """
        Fork a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            organization: Organization to fork to (optional)
            
        Returns:
            Forked repository details
        """
        self._track_request()
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN not set")
        
        payload = {}
        if organization:
            payload["organization"] = organization
        
        session = await self._get_session()
        async with session.post(
            f"{self.api_url}/repos/{owner}/{repo}/forks",
            headers=self._headers(),
            json=payload
        ) as resp:
            if resp.status == 202:
                return await resp.json()
            else:
                text = await resp.text()
                raise Exception(f"GitHub fork failed: {resp.status} - {text}")
