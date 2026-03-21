#!/usr/bin/env python3
"""
Kimi MCP Client - Full Implementation Demo
Demonstrates real usage of all 8 MCP servers
"""

import asyncio
from kimi_mcp_client import KimiMCPClient


async def demo_basic_usage():
    """Demonstrate basic client usage."""
    print("=" * 70)
    print("KIMI MCP CLIENT - FULL IMPLEMENTATION DEMO")
    print("=" * 70)
    
    # Initialize client with yolo mode
    print("\n🚀 Initializing KimiMCPClient (yolo_mode=True)...")
    client = KimiMCPClient(yolo_mode=True)
    
    # Initialize all servers
    status = await client.initialize()
    print(f"✅ Initialized {len(status)} servers\n")
    
    # Display server status
    print("-" * 70)
    print("SERVER STATUS")
    print("-" * 70)
    for server, info in status.items():
        icon = "✅" if info.get("status") == "healthy" else "❌"
        print(f"{icon} {server:20s} {info.get('status', 'unknown')}")
    
    return client


async def demo_perplexity(client: KimiMCPClient):
    """Demo Perplexity server."""
    print("\n" + "=" * 70)
    print("1. PERPLEXITY SERVER - Research & Q&A")
    print("=" * 70)
    
    # Quick question
    print("\n🔍 Asking: 'What are MCP servers?'")
    answer = await client.perplexity.ask("What are MCP servers?")
    print(f"✅ Answer received: {len(answer.get('answer', ''))} chars")
    
    # Deep research
    print("\n📚 Researching: 'Best practices for AI agents'")
    research = await client.perplexity.research("Best practices for AI agents")
    print(f"✅ Research complete: {research.get('depth', '')} depth")
    
    # Reasoning
    print("\n🧠 Reasoning about: 'Should I use REST or GraphQL?'")
    reasoning = await client.perplexity.reason("Should I use REST or GraphQL?")
    print(f"✅ Reasoning complete: {reasoning.get('confidence', 0)} confidence")


async def demo_linear(client: KimiMCPClient):
    """Demo Linear server."""
    print("\n" + "=" * 70)
    print("2. LINEAR SERVER - Issue Tracking")
    print("=" * 70)
    
    # Get teams
    print("\n📋 Getting teams...")
    teams = await client.linear.get_teams()
    print(f"✅ Found {len(teams)} teams")
    
    # Create issue
    print("\n📝 Creating issue...")
    issue = await client.linear.create_issue(
        title="MCP Client Demo Issue",
        description="This issue was created via the Kimi MCP Client",
        team_id="2d851660-3f0d-4be2-9555-dcbaf55bf8fa",
        priority=3
    )
    print(f"✅ Created: {issue['identifier']}")
    print(f"   URL: {issue['url']}")


async def demo_github(client: KimiMCPClient):
    """Demo GitHub server."""
    print("\n" + "=" * 70)
    print("3. GITHUB SERVER - Code Operations")
    print("=" * 70)
    
    # Search code
    print("\n🔍 Searching code...")
    results = await client.github.search_code(
        query="filename:README.md repo:Nietzsche-Ubermensch/kimi-cli-tools"
    )
    print(f"✅ Found {results.get('total_count', 0)} results")
    
    # Create PR
    print("\n📦 Creating PR...")
    pr = await client.github.create_pull_request(
        owner="Nietzsche-Ubermensch",
        repo="kimi-cli-tools",
        title="Demo: MCP Client Integration",
        head="feature/demo",
        base="main",
        body="This PR demonstrates the Kimi MCP Client"
    )
    print(f"✅ Created PR #{pr['number']}")
    print(f"   URL: {pr['html_url']}")
    
    # Push files
    print("\n📤 Pushing files...")
    commit = await client.github.push_files(
        owner="Nietzsche-Ubermensch",
        repo="kimi-cli-tools",
        branch="main",
        files=[
            {"path": "demo/file1.txt", "content": "Hello from MCP"},
            {"path": "demo/file2.txt", "content": "Kimi MCP Client demo"}
        ],
        message="feat: add MCP client demo files"
    )
    print(f"✅ Committed: {commit['commit']['sha'][:8]}")


async def demo_brave(client: KimiMCPClient):
    """Demo Brave Search server."""
    print("\n" + "=" * 70)
    print("4. BRAVE SEARCH SERVER - Web Discovery")
    print("=" * 70)
    
    # Web search
    print("\n🦁 Searching: 'MCP Model Context Protocol'")
    results = await client.brave.web_search("MCP Model Context Protocol")
    print(f"✅ Found {results.get('total', 0)} results")
    
    # Display first few results
    for i, result in enumerate(results.get('results', [])[:3], 1):
        print(f"   {i}. {result.get('title', 'No title')}")


async def demo_firecrawl(client: KimiMCPClient):
    """Demo Firecrawl server."""
    print("\n" + "=" * 70)
    print("5. FIRECRAWL SERVER - Web Scraping")
    print("=" * 70)
    
    # Scrape page
    print("\n🔥 Scraping: https://modelcontextprotocol.io")
    page = await client.firecrawl.scrape(
        url="https://modelcontextprotocol.io",
        formats=["markdown"],
        only_main_content=True
    )
    print(f"✅ Scraped: {page.get('url')}")
    print(f"   Title: {page.get('metadata', {}).get('title', 'N/A')}")
    
    # Map URLs
    print("\n🗺️ Mapping URLs...")
    urls = await client.firecrawl.map("https://modelcontextprotocol.io")
    print(f"✅ Found {len(urls)} URLs")


async def demo_chrome(client: KimiMCPClient):
    """Demo Chrome DevTools server."""
    print("\n" + "=" * 70)
    print("6. CHROME DEVTOOLS SERVER - Browser Automation")
    print("=" * 70)
    
    # Navigate
    print("\n🧪 Navigating to example.com...")
    nav = await client.chrome.navigate("https://example.com")
    print(f"✅ Loaded: {nav.get('title')} ({nav.get('status')})")
    
    # Screenshot
    print("\n📸 Capturing screenshot...")
    screenshot = await client.chrome.screenshot(full_page=True)
    print(f"✅ Screenshot: {screenshot.get('size')}")
    
    # Get snapshot
    print("\n📋 Getting page snapshot...")
    snapshot = await client.chrome.snapshot()
    print(f"✅ Snapshot: {snapshot.get('title')}")


async def demo_playwright(client: KimiMCPClient):
    """Demo Playwright server."""
    print("\n" + "=" * 70)
    print("7. PLAYWRIGHT SERVER - Cross-Browser Testing")
    print("=" * 70)
    
    # New page
    print("\n🎭 Creating new page...")
    page = await client.playwright.new_page(browser="chromium")
    print(f"✅ Page created: {page.get('page_id')}")
    
    # Navigate
    print("\n🌐 Navigating...")
    await client.playwright.goto(page['page_id'], "https://example.com")
    print("✅ Navigation complete")
    
    # Find element by role
    print("\n🔍 Finding element by role...")
    element = await client.playwright.get_by_role(
        page['page_id'],
        role="button",
        name="Submit"
    )
    print(f"✅ Element found: {element.get('found')}")


async def demo_context7(client: KimiMCPClient):
    """Demo Context7 server."""
    print("\n" + "=" * 70)
    print("8. CONTEXT7 SERVER - Documentation Lookup")
    print("=" * 70)
    
    # List libraries
    print("\n📚 Listing available libraries...")
    libs = await client.context7.list_libraries()
    print(f"✅ Available: {', '.join(libs[:5])}...")
    
    # Resolve library
    print("\n🔍 Resolving: nextjs")
    lib_info = await client.context7.resolve_library("nextjs", "app router")
    print(f"✅ Library ID: {lib_info.get('library_id')}")
    
    # Query docs
    print("\n📖 Querying documentation...")
    answer = await client.context7.query_docs(
        library_id="/docs/nextjs",
        question="How to use the app router?"
    )
    print(f"✅ Answer: {len(answer.get('answer', ''))} chars")


async def demo_workflows(client: KimiMCPClient):
    """Demo pre-built workflows."""
    print("\n" + "=" * 70)
    print("PRE-BUILT WORKFLOWS")
    print("=" * 70)
    
    # Research to Linear
    print("\n🔄 Workflow: Research → Linear Issue")
    print("-" * 70)
    result = await client.workflows.research_to_linear(
        topic="React Server Components",
        team_id="2d851660-3f0d-4be2-9555-dcbaf55bf8fa"
    )
    print(f"✅ Created issue: {result['issue']['identifier']}")
    
    # Session report
    print("\n" + "=" * 70)
    print("SESSION REPORT")
    print("=" * 70)
    report = client.get_session_report()
    print(f"Started: {report['started_at']}")
    print(f"Duration: {report['duration_seconds']}s")
    print(f"Servers used: {', '.join(report['servers_used'])}")
    print(f"Actions taken: {report['actions_taken']}")
    print(f"Yolo mode: {report['yolo_mode']}")


async def main():
    """Run full demo."""
    # Initialize
    client = await demo_basic_usage()
    
    # Demo each server
    await demo_perplexity(client)
    await demo_linear(client)
    await demo_github(client)
    await demo_brave(client)
    await demo_firecrawl(client)
    await demo_chrome(client)
    await demo_playwright(client)
    await demo_context7(client)
    
    # Demo workflows
    await demo_workflows(client)
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
