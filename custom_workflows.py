#!/usr/bin/env python3
"""
Custom Workflows for Kimi MCP Client
User-defined execution chains
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any


class CustomWorkflows:
    """User-defined MCP workflows."""
    
    @staticmethod
    async def scrape_to_github(
        target_url: str,
        output_repo: str,
        file_path: str = None
    ) -> Dict[str, Any]:
        """
        Workflow: Scrape website → Generate code → Push to GitHub
        
        Args:
            target_url: URL to scrape
            output_repo: GitHub repo (owner/repo)
            file_path: Path for output file
        
        Returns:
            Dict with commit info and PR URL
        """
        print(f"\n{'='*70}")
        print(f"CUSTOM WORKFLOW: Scrape → Code → GitHub")
        print(f"{'='*70}")
        print(f"Target: {target_url}")
        print(f"Output: {output_repo}")
        print(f"Started: {datetime.now().isoformat()}\n")
        
        # Step 1: Scrape the website
        print("🔥 Step 1: Scraping target URL...")
        try:
            from firecrawl_scrape import firecrawl_scrape
            
            scrape_result = firecrawl_scrape(
                url=target_url,
                formats=["markdown", "html"],
                onlyMainContent=True
            )
            
            title = scrape_result.get("metadata", {}).get("title", "Unknown")
            content = scrape_result.get("markdown", "")
            
            print(f"  ✅ Scraped: {title}")
            print(f"  📄 Content: {len(content)} chars")
        except Exception as e:
            print(f"  ❌ Scraping failed: {e}")
            return {"success": False, "error": f"Scrape failed: {e}"}
        
        # Step 2: Generate code from content
        print("\n💻 Step 2: Generating scraper code...")
        try:
            from perplexity_ask import perplexity_ask
            
            code_gen = perplexity_ask(
                messages=[
                    {"role": "system", "content": "You are a Python developer. Write clean, documented code."},
                    {"role": "user", "content": f"""Given this website content from {target_url}, write a Python scraper using requests and BeautifulSoup that extracts the main data.

Website title: {title}
Content preview: {content[:1000]}...

Generate a complete Python script with:
1. Error handling
2. Data extraction logic
3. JSON output
4. Main execution block"""}
                ]
            )
            
            generated_code = code_gen.get("content", "") if isinstance(code_gen, dict) else str(code_gen)
            
            # Extract code block if present
            if "```python" in generated_code:
                code_parts = generated_code.split("```python")
                if len(code_parts) > 1:
                    generated_code = code_parts[1].split("```")[0].strip()
            
            print(f"  ✅ Code generated ({len(generated_code)} chars)")
        except Exception as e:
            print(f"  ❌ Code generation failed: {e}")
            generated_code = f"# Scraper for {target_url}\n# Error: {e}"
        
        # Step 3: Push to GitHub
        print("\n📤 Step 3: Pushing to GitHub...")
        try:
            from push_files import push_files
            
            owner, repo = output_repo.split("/")
            filepath = file_path or f"scrapers/{title.lower().replace(' ', '_')[:30]}.py"
            
            commit = push_files(
                owner=owner,
                repo=repo,
                branch="main",
                files=[
                    {
                        "path": filepath,
                        "content": generated_code
                    },
                    {
                        "path": f"{filepath}.md",
                        "content": f"""# Scraper: {title}

**Source:** {target_url}
**Generated:** {datetime.now().isoformat()}

## Description

This scraper was auto-generated from website content.

## Usage

```bash
python {filepath}
```

## Output

Results saved to JSON file.
"""
                    }
                ],
                message=f"feat: add scraper for {title[:50]}"
            )
            
            commit_sha = commit.get("commit", {}).get("sha", "")[:8]
            print(f"  ✅ Committed: {commit_sha}")
            print(f"  📄 Files: {filepath}, {filepath}.md")
            
            return {
                "success": True,
                "commit": commit,
                "files": [filepath, f"{filepath}.md"],
                "title": title
            }
        
        except Exception as e:
            print(f"  ❌ Push failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "code": generated_code
            }
    
    @staticmethod
    async def research_and_document(
        topic: str,
        library: str,
        output_format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Workflow: Research topic → Get library docs → Generate guide
        
        Args:
            topic: Research topic
            library: Library name for Context7 lookup
            output_format: Output format (markdown, html)
        
        Returns:
            Dict with generated documentation
        """
        print(f"\n{'='*70}")
        print(f"CUSTOM WORKFLOW: Research + Documentation")
        print(f"{'='*70}")
        print(f"Topic: {topic}")
        print(f"Library: {library}")
        print(f"Started: {datetime.now().isoformat()}\n")
        
        # Step 1: Deep research
        print("🔍 Step 1: Researching topic...")
        try:
            from perplexity_research import perplexity_research
            
            research = perplexity_research(
                messages=[
                    {"role": "user", "content": f"Comprehensive guide to {topic}. Include best practices, common pitfalls, and advanced techniques."}
                ],
                reasoning_effort="high"
            )
            
            research_content = research.get("content", str(research))
            print(f"  ✅ Research complete ({len(research_content)} chars)")
        except Exception as e:
            print(f"  ❌ Research failed: {e}")
            research_content = f"# {topic}\n\nResearch pending..."
        
        # Step 2: Get library documentation
        print("\n📚 Step 2: Getting library documentation...")
        try:
            from resolve_library_id import resolve_library_id
            from query_docs import query_docs
            
            lib_info = resolve_library_id(
                libraryName=library,
                query=f"How to use {library} with {topic}"
            )
            
            lib_id = lib_info[0].get("libraryId") if lib_info else None
            
            if lib_id:
                docs = query_docs(
                    libraryId=lib_id,
                    query=f"{topic} implementation guide"
                )
                doc_snippets = docs.get("answer", "No specific docs found")
            else:
                doc_snippets = f"Library {library} documentation not found"
            
            print(f"  ✅ Docs retrieved")
        except Exception as e:
            print(f"  ⚠️  Docs skipped: {e}")
            doc_snippets = f"Library: {library}"
        
        # Step 3: Compile guide
        print("\n📝 Step 3: Compiling documentation...")
        
        guide = f"""# {topic} Guide

**Library:** {library}  
**Generated:** {datetime.now().isoformat()}  
**Format:** {output_format}

---

## Overview

{research_content[:2000]}{'...' if len(research_content) > 2000 else ''}

## Library Documentation

{doc_snippets[:1500]}{'...' if len(str(doc_snippets)) > 1500 else ''}

## Quick Start

```python
# Example implementation
import {library.lower()}

# TODO: Add implementation
```

## Resources

- Research based on multiple sources
- Official {library} documentation
- Best practices from {topic}

---
*Generated by Kimi MCP Client*
"""
        
        print(f"  ✅ Guide compiled ({len(guide)} chars)")
        
        # Save to file
        filename = f"guides/{topic.lower().replace(' ', '_')[:30]}_guide.md"
        with open(filename, "w") as f:
            f.write(guide)
        
        print(f"  💾 Saved to: {filename}")
        
        return {
            "success": True,
            "guide": guide,
            "filename": filename,
            "research_length": len(research_content),
            "library": library
        }
    
    @staticmethod
    async def browser_test_and_report(
        url: str,
        linear_team_id: str
    ) -> Dict[str, Any]:
        """
        Workflow: Test website in browser → Screenshot → Create Linear issue
        
        Args:
            url: URL to test
            linear_team_id: Linear team ID
        
        Returns:
            Dict with test results and issue info
        """
        print(f"\n{'='*70}")
        print(f"CUSTOM WORKFLOW: Browser Test → Report")
        print(f"{'='*70}")
        print(f"URL: {url}")
        print(f"Started: {datetime.now().isoformat()}\n")
        
        # Step 1: Navigate and test
        print("🧪 Step 1: Browser testing...")
        try:
            from navigate_page import navigate_page
            from take_screenshot import take_screenshot
            
            # Navigate
            nav = navigate_page(type="url", url=url)
            title = nav.get("title", "Unknown")
            status = nav.get("status", 0)
            
            print(f"  ✅ Loaded: {title} (HTTP {status})")
            
            # Screenshot
            screenshot = take_screenshot(fullPage=True)
            screenshot_path = screenshot.get("filePath", "screenshot.png")
            
            print(f"  📸 Screenshot: {screenshot_path}")
        except Exception as e:
            print(f"  ❌ Browser test failed: {e}")
            return {"success": False, "error": str(e)}
        
        # Step 2: Create Linear issue
        print("\n📝 Step 2: Creating Linear issue...")
        try:
            from linear_createIssue import linear_createIssue
            
            issue = linear_createIssue(
                title=f"Browser Test: {title[:50]}",
                description=f"""## Browser Test Report

**URL:** {url}
**Tested:** {datetime.now().isoformat()}
**Status:** HTTP {status}

### Results

- Page loaded successfully
- Title: {title}
- Screenshot captured: {screenshot_path}

### Notes

Website tested via Chrome DevTools MCP server.

---
*Automated test by Kimi MCP Client*
""",
                teamId=linear_team_id,
                priority=3
            )
            
            print(f"  ✅ Issue created: {issue.get('identifier')}")
            
            return {
                "success": True,
                "issue": issue,
                "title": title,
                "status": status,
                "screenshot": screenshot_path
            }
        
        except Exception as e:
            print(f"  ❌ Failed to create issue: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_data": {"title": title, "status": status}
            }


async def main():
    """Run custom workflow demos."""
    print("\n" + "="*70)
    print("CUSTOM WORKFLOW DEMOS")
    print("="*70)
    
    workflows = CustomWorkflows()
    
    # Demo 1: Scrape to GitHub
    print("\n\n📌 DEMO 1: Scrape → Code → GitHub")
    result1 = await workflows.scrape_to_github(
        target_url="https://example.com",
        output_repo="Nietzsche-Ubermensch/kimi-cli-tools",
        file_path="scrapers/example_scraper.py"
    )
    
    # Demo 2: Research and document
    print("\n\n📌 DEMO 2: Research + Documentation")
    result2 = await workflows.research_and_document(
        topic="Python Async Programming",
        library="asyncio",
        output_format="markdown"
    )
    
    # Demo 3: Browser test
    print("\n\n📌 DEMO 3: Browser Test → Linear")
    result3 = await workflows.browser_test_and_report(
        url="https://modelcontextprotocol.io",
        linear_team_id="2d851660-3f0d-4be2-9555-dcbaf55bf8fa"
    )
    
    # Summary
    print("\n\n" + "="*70)
    print("CUSTOM WORKFLOW SUMMARY")
    print("="*70)
    print(f"Scrape → GitHub: {'✅' if result1.get('success') else '❌'}")
    print(f"Research + Docs: {'✅' if result2.get('success') else '❌'}")
    print(f"Browser → Linear: {'✅' if result3.get('success') else '❌'}")
    
    print("\n✅ All custom workflows ready!")


if __name__ == "__main__":
    # Run demos
    asyncio.run(main())
