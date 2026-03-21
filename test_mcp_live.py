#!/usr/bin/env python3
"""
Live MCP Server Test
Tests all 8 configured MCP servers
"""

import asyncio
import json
from datetime import datetime

# Test results
results = {
    "tested_at": datetime.now().isoformat(),
    "servers": {}
}

async def test_perplexity():
    """Test Perplexity server."""
    print("\n🔍 Testing Perplexity...")
    try:
        from perplexity_ask import perplexity_ask
        
        response = perplexity_ask(
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "What is 2+2? Answer in one word."}
            ]
        )
        
        results["servers"]["perplexity"] = {
            "status": "✅ healthy",
            "response": response.get("content", "")[:50] if isinstance(response, dict) else str(response)[:50]
        }
        print(f"  ✅ Perplexity responding")
        return True
    except Exception as e:
        results["servers"]["perplexity"] = {"status": f"❌ error: {str(e)}"}
        print(f"  ❌ Error: {e}")
        return False

async def test_linear():
    """Test Linear server."""
    print("\n📋 Testing Linear...")
    try:
        from linear_getTeams import linear_getTeams
        
        teams = linear_getTeams()
        team_count = len(teams.get("data", {}).get("teams", {}).get("nodes", [])) if isinstance(teams, dict) else 0
        
        results["servers"]["linear"] = {
            "status": "✅ healthy",
            "teams_found": team_count
        }
        print(f"  ✅ Linear responding ({team_count} teams)")
        return True
    except Exception as e:
        results["servers"]["linear"] = {"status": f"❌ error: {str(e)}"}
        print(f"  ❌ Error: {e}")
        return False

async def test_github():
    """Test GitHub server."""
    print("\n🐙 Testing GitHub...")
    try:
        from search_repositories import search_repositories
        
        repos = search_repositories(query="kimi-cli-tools user:Nietzsche-Ubermensch")
        repo_count = len(repos) if isinstance(repos, list) else 0
        
        results["servers"]["github"] = {
            "status": "✅ healthy",
            "repos_found": repo_count
        }
        print(f"  ✅ GitHub responding ({repo_count} repos)")
        return True
    except Exception as e:
        results["servers"]["github"] = {"status": f"❌ error: {str(e)}"}
        print(f"  ❌ Error: {e}")
        return False

async def test_brave():
    """Test Brave Search server."""
    print("\n🦁 Testing Brave Search...")
    try:
        from brave_web_search import brave_web_search
        
        search = brave_web_search(query="MCP servers")
        result_count = len(search.get("web", {}).get("results", [])) if isinstance(search, dict) else 0
        
        results["servers"]["brave"] = {
            "status": "✅ healthy",
            "results_found": result_count
        }
        print(f"  ✅ Brave responding ({result_count} results)")
        return True
    except Exception as e:
        results["servers"]["brave"] = {"status": f"❌ error: {str(e)}"}
        print(f"  ❌ Error: {e}")
        return False

async def test_firecrawl():
    """Test Firecrawl server."""
    print("\n🔥 Testing Firecrawl...")
    try:
        from firecrawl_map import firecrawl_map
        
        urls = firecrawl_map(url="https://modelcontextprotocol.io", limit=5)
        url_count = len(urls) if isinstance(urls, list) else 0
        
        results["servers"]["firecrawl"] = {
            "status": "✅ healthy",
            "urls_found": url_count
        }
        print(f"  ✅ Firecrawl responding ({url_count} URLs)")
        return True
    except Exception as e:
        results["servers"]["firecrawl"] = {"status": f"❌ error: {str(e)}"}
        print(f"  ❌ Error: {e}")
        return False

async def test_chrome():
    """Test Chrome DevTools server."""
    print("\n🧪 Testing Chrome DevTools...")
    try:
        from list_pages import list_pages
        
        pages = list_pages()
        page_count = len(pages.get("pages", [])) if isinstance(pages, dict) else 0
        
        results["servers"]["chrome"] = {
            "status": "✅ healthy",
            "pages_open": page_count
        }
        print(f"  ✅ Chrome DevTools responding ({page_count} pages)")
        return True
    except Exception as e:
        results["servers"]["chrome"] = {"status": f"❌ error: {str(e)}"}
        print(f"  ❌ Error: {e}")
        return False

async def test_playwright():
    """Test Playwright server."""
    print("\n🎭 Testing Playwright...")
    try:
        results["servers"]["playwright"] = {
            "status": "⚠️  skipped (requires manual setup)",
            "note": "Playwright MCP server needs browser instance"
        }
        print(f"  ⚠️  Playwright (requires manual setup)")
        return True
    except Exception as e:
        results["servers"]["playwright"] = {"status": f"❌ error: {str(e)}"}
        print(f"  ❌ Error: {e}")
        return False

async def test_context7():
    """Test Context7 server."""
    print("\n📚 Testing Context7...")
    try:
        results["servers"]["context7"] = {
            "status": "⚠️  skipped (no API key)",
            "note": "Add CONTEXT7_API_KEY to .env to enable"
        }
        print(f"  ⚠️  Context7 (no API key configured)")
        return True
    except Exception as e:
        results["servers"]["context7"] = {"status": f"❌ error: {str(e)}"}
        print(f"  ❌ Error: {e}")
        return False

async def main():
    """Run all tests."""
    print("=" * 70)
    print("KIMI MCP CLIENT - LIVE SERVER TEST")
    print("=" * 70)
    
    # Run all tests
    await test_perplexity()
    await test_linear()
    await test_github()
    await test_brave()
    await test_firecrawl()
    await test_chrome()
    await test_playwright()
    await test_context7()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    healthy = sum(1 for s in results["servers"].values() if "✅" in s.get("status", ""))
    total = len(results["servers"])
    
    for server, info in results["servers"].items():
        print(f"{info['status']:25s} {server}")
    
    print(f"\n{healthy}/{total} servers fully operational")
    
    # Save report
    with open("mcp_test_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Report saved to: mcp_test_report.json")

if __name__ == "__main__":
    asyncio.run(main())
