"""
MCP Workflow Implementations
Full execution chains using real MCP server tools
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .client import KimiMCPClient


class MCPWorkflows:
    """
    Pre-built MCP server execution chains.
    
    Usage:
        client = KimiMCPClient()
        await client.workflows.research_to_linear("topic", team_id)
    """
    
    def __init__(self, client: "KimiMCPClient"):
        self.client = client
    
    async def research_to_linear(
        self,
        topic: str,
        team_id: str,
        priority: int = 2
    ) -> Dict[str, Any]:
        """
        Workflow: Research → Create Linear Issue
        
        1. Use Perplexity to research topic
        2. Create Linear issue with findings
        
        Args:
            topic: Topic to research
            team_id: Linear team ID
            priority: Issue priority (0-4)
            
        Returns:
            Research results and created issue
        """
        print(f"🔍 Workflow: Research → Linear Issue")
        print(f"   Topic: {topic}")
        
        # Step 1: Research with Perplexity
        print("   Step 1/2: Researching with Perplexity...")
        research = await self.client.perplexity.research(topic)
        
        # Step 2: Create Linear issue
        print("   Step 2/2: Creating Linear issue...")
        issue = await self.client.linear.create_issue(
            title=f"Research: {topic}",
            description=research.get("summary", ""),
            team_id=team_id,
            priority=priority
        )
        
        print(f"✅ Created: {issue['identifier']}")
        
        return {
            "workflow": "research_to_linear",
            "topic": topic,
            "research": research,
            "issue": issue
        }
    
    async def bug_fix(
        self,
        issue_id: str,
        repo: str
    ) -> Dict[str, Any]:
        """
        Workflow: Bug Fix with PR
        
        1. Read Linear issue
        2. Search GitHub for failing code
        3. Research fix
        4. Create PR
        5. Update Linear issue
        
        Args:
            issue_id: Linear issue identifier
            repo: GitHub repo (owner/name)
            
        Returns:
            Full workflow results
        """
        print(f"🐛 Workflow: Bug Fix")
        print(f"   Issue: {issue_id}")
        print(f"   Repo: {repo}")
        
        # Step 1: Get issue details
        # BUG-004 FIX: was a hardcoded stub — now actually fetches from Linear.
        print("   Step 1/5: Reading Linear issue...")
        issue = await self.client.linear.get_issue(issue_id)
        
        # Step 2: Search codebase
        print("   Step 2/5: Searching GitHub code...")
        code_results = await self.client.github.search_code(
            query=f"repo:{repo} {issue['title']}"
        )
        
        # Step 3: Research fix
        print("   Step 3/5: Researching fix approach...")
        solution = await self.client.perplexity.ask(
            f"How to fix: {issue['description']}"
        )
        
        # Step 4: Create PR
        print("   Step 4/5: Creating PR...")
        owner, repo_name = repo.split("/")
        pr = await self.client.github.create_pull_request(
            owner=owner,
            repo=repo_name,
            title=f"Fix: {issue['title']}",
            body=f"Closes {issue_id}\n\n{solution.get('answer', '')}",
            head=f"fix/{issue_id.lower().replace('-', '_')}",
            base="main"
        )
        
        # Step 5: Update Linear
        print("   Step 5/5: Updating Linear issue...")
        await self.client.linear.update_issue(
            issue_id=issue_id,
            description=f"{issue['description']}\n\nPR: {pr['html_url']}"
        )
        
        print(f"✅ Created PR: {pr['number']}")
        
        return {
            "workflow": "bug_fix",
            "issue": issue,
            "code_search": code_results,
            "solution": solution,
            "pr": pr
        }
    
    async def competitive_analysis(
        self,
        query: str,
        team_id: str,
        num_competitors: int = 3
    ) -> Dict[str, Any]:
        """
        Workflow: Competitive Analysis
        
        1. Brave Search for competitors
        2. Firecrawl competitor pages
        3. Perplexity deep research
        4. Create Linear issue with summary
        
        Args:
            query: Search query for competitors
            team_id: Linear team ID
            num_competitors: Number to analyze
            
        Returns:
            Analysis results
        """
        print(f"🦁 Workflow: Competitive Analysis")
        print(f"   Query: {query}")
        
        # Step 1: Find competitors
        print(f"   Step 1/4: Searching for competitors...")
        search_results = await self.client.brave.web_search(
            query=f"top {query} competitors"
        )
        
        # Step 2: Scrape competitor pages
        print(f"   Step 2/4: Scraping competitor pages...")
        competitors = search_results.get("results", [])[:num_competitors]
        scraped = []
        for comp in competitors:
            # BUG-005 FIX: Brave Search returns results under "web.results";
            # each result uses "url" but fall back to "link" defensively.
            # Skip entries where no URL can be determined.
            comp_url = comp.get("url") or comp.get("link")
            if not comp_url:
                continue
            page = await self.client.firecrawl.scrape(
                url=comp_url,
                formats=["markdown"]
            )
            scraped.append(page)
        
        # Step 3: Analyze
        print(f"   Step 3/4: Analyzing with Perplexity...")
        analysis = await self.client.perplexity.research(
            topic=f"Analysis of {query} competitors"
        )
        
        # Step 4: Create issue
        print(f"   Step 4/4: Creating Linear issue...")
        issue = await self.client.linear.create_issue(
            title=f"Competitive Analysis: {query}",
            description=analysis.get("summary", ""),
            team_id=team_id,
            priority=3
        )
        
        print(f"✅ Created: {issue['identifier']}")
        
        return {
            "workflow": "competitive_analysis",
            "competitors": competitors,
            "scraped_pages": scraped,
            "analysis": analysis,
            "issue": issue
        }
    
    async def scraper_build(
        self,
        target_url: str,
        output_repo: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Workflow: Build and Deploy Scraper
        
        1. Research target with Perplexity
        2. Test extraction with Firecrawl
        3. Generate scraper code
        4. Push to GitHub
        
        Args:
            target_url: URL to scrape
            output_repo: GitHub repo for output
            branch: Target branch
            
        Returns:
            Build results
        """
        print(f"🔥 Workflow: Build Scraper")
        print(f"   Target: {target_url}")
        print(f"   Output: {output_repo}")
        
        # Step 1: Research
        print("   Step 1/4: Researching target...")
        research = await self.client.perplexity.ask(
            f"What is the structure of {target_url}?"
        )
        
        # Step 2: Test extraction
        print("   Step 2/4: Testing extraction...")
        test = await self.client.firecrawl.scrape(
            url=target_url,
            formats=["markdown"]
        )
        
        # Step 3: Generate code
        print("   Step 3/4: Generating scraper code...")
        scraper_code = self._generate_scraper_code(target_url)
        
        # Step 4: Push to GitHub
        print("   Step 4/4: Pushing to GitHub...")
        # BUG-006 FIX: split("/") on a URL without "://" raises IndexError[1].
        # Use urllib.parse for robust URL decomposition.
        from urllib.parse import urlparse
        parsed = urlparse(target_url if "://" in target_url else f"https://{target_url}")
        safe_name = (parsed.netloc + parsed.path).replace("/", "_").strip("_") or "unknown"

        if "/" not in output_repo:
            raise ValueError(f"output_repo must be 'owner/repo', got: {output_repo!r}")
        owner, repo = output_repo.split("/", 1)

        commit = await self.client.github.push_files(
            owner=owner,
            repo=repo,
            branch=branch,
            files=[{
                "path": f"scrapers/{safe_name}.py",
                "content": scraper_code
            }],
            message=f"Add scraper for {target_url}"
        )
        
        print(f"✅ Committed: {commit['commit']['sha'][:8]}")
        
        return {
            "workflow": "scraper_build",
            "research": research,
            "test_extraction": test,
            "code": scraper_code,
            "commit": commit
        }
    
    def _generate_scraper_code(self, url: str) -> str:
        """Generate Python scraper code."""
        # BUG-007 FIX: same split("//")[1] IndexError as BUG-006.
        from urllib.parse import urlparse
        parsed = urlparse(url if "://" in url else f"https://{url}")
        domain = (parsed.netloc or url).replace(".", "_").replace("-", "_")
        
        return f'''#!/usr/bin/env python3
"""
Auto-generated scraper for {url}
Generated: {datetime.now().isoformat()}
"""

import requests
from bs4 import BeautifulSoup
import json

TARGET_URL = "{url}"

def scrape():
    """Scrape data from target URL."""
    headers = {{
        "User-Agent": "Mozilla/5.0 (compatible; KimiBot/1.0)"
    }}
    
    response = requests.get(TARGET_URL, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # TODO: Add extraction logic
    data = {{
        "url": TARGET_URL,
        "title": soup.title.string if soup.title else None,
        "content": soup.get_text()[:1000]
    }}
    
    return data

if __name__ == "__main__":
    result = scrape()
    print(json.dumps(result, indent=2))
'''
    
    async def documentation_lookup(
        self,
        library: str,
        question: str
    ) -> Dict[str, Any]:
        """
        Workflow: Library Documentation Lookup
        
        1. Resolve library with Context7
        2. Query documentation
        3. Return answer with code examples
        
        Args:
            library: Library name (e.g., "nextjs", "react")
            question: Specific question
            
        Returns:
            Documentation answer
        """
        print(f"📚 Workflow: Documentation Lookup")
        print(f"   Library: {library}")
        print(f"   Question: {question}")
        
        # Step 1: Resolve library
        print("   Step 1/2: Resolving library...")
        lib_info = await self.client.context7.resolve_library(
            library_name=library,
            query=question
        )
        
        # Step 2: Query docs
        print("   Step 2/2: Querying documentation...")
        answer = await self.client.context7.query_docs(
            library_id=lib_info.get("library_id", ""),
            query=question
        )
        
        print(f"✅ Found answer")
        
        return {
            "workflow": "documentation_lookup",
            "library": lib_info,
            "answer": answer
        }
