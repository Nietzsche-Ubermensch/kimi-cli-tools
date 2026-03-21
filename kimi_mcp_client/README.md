# Kimi MCP Client

Full implementation of 8-server MCP orchestration for Kimi CLI.

## 🚀 Quick Start

```bash
# Install
pip install -e .

# Check status
kimi-mcp status

# Run workflow
kimi-mcp workflow research_to_linear "React 19 features" "team-id"

# Interactive mode
kimi-mcp interactive
```

## 📦 Package Structure

```
kimi_mcp_client/
├── __init__.py          # Package exports
├── client.py            # Main KimiMCPClient class
├── cli.py               # Command-line interface
├── workflows.py         # Pre-built execution chains
├── servers/             # Server implementations
│   ├── __init__.py
│   ├── base.py          # BaseMCPServer
│   ├── perplexity.py    # Research & Q&A
│   ├── linear.py        # Issue tracking
│   ├── github.py        # Code operations
│   ├── brave.py         # Web search
│   ├── firecrawl.py     # Web scraping
│   ├── chrome.py        # Browser automation
│   ├── playwright.py    # Cross-browser testing
│   └── context7.py      # Documentation lookup
├── requirements.txt
├── setup.py
└── README.md
```

## 🔌 8 MCP Servers

| Server | Purpose | Key Tools |
|--------|---------|-----------|
| **Perplexity** | Research, Q&A | `ask`, `research`, `reason` |
| **Linear** | Issue tracking | `create_issue`, `update_issue`, `search_issues` |
| **GitHub** | Code operations | `search_code`, `create_pr`, `push_files` |
| **Brave** | Web search | `web_search`, `image_search`, `news_search` |
| **Firecrawl** | Web scraping | `scrape`, `crawl`, `extract` |
| **Chrome DevTools** | Browser automation | `navigate`, `click`, `screenshot` |
| **Playwright** | Cross-browser testing | `new_page`, `goto`, `expect` |
| **Context7** | Documentation | `resolve_library`, `query_docs` |

## 🔄 Workflows

### 1. Research → Linear Issue
```python
from kimi_mcp_client import KimiMCPClient

client = KimiMCPClient(yolo_mode=True)
await client.initialize()

result = await client.workflows.research_to_linear(
    topic="React 19 features",
    team_id="your-team-id"
)
```

### 2. Bug Fix with PR
```python
result = await client.workflows.bug_fix(
    issue_id="KIM-123",
    repo="owner/repo"
)
```

### 3. Competitive Analysis
```python
result = await client.workflows.competitive_analysis(
    query="AI coding assistants",
    team_id="your-team-id"
)
```

### 4. Build Scraper
```python
result = await client.workflows.scraper_build(
    target_url="https://example.com",
    output_repo="owner/scrapers"
)
```

## 🔧 Direct Server Access

```python
# Research
answer = await client.perplexity.ask("What is MCP?")

# Create issue
issue = await client.linear.create_issue(
    title="New feature",
    team_id="team-id"
)

# Search code
results = await client.github.search_code(
    query="filename:package.json repo:owner/repo"
)

# Scrape page
content = await client.firecrawl.scrape(
    url="https://example.com",
    formats=["markdown"]
)

# Search web
results = await client.brave.web_search("MCP servers")

# Browser automation
await client.chrome.navigate("https://example.com")
await client.chrome.screenshot(full_page=True)
```

## 🛠️ Configuration

Environment variables:
```bash
PERPLEXITY_API_KEY=pplx-...
LINEAR_API_KEY=lin_api_...
GITHUB_TOKEN=ghp_...
BRAVE_API_KEY=BSA...
FIRECRAWL_API_KEY=fc-...
CONTEXT7_API_KEY=...
```

## 📊 Session Tracking

```python
# Get session report
report = client.get_session_report()
print(report)
# {
#   "started_at": "2026-03-20T...",
#   "duration_seconds": 120,
#   "servers_used": ["perplexity", "linear"],
#   "actions_taken": 5,
#   "yolo_mode": true
# }
```

## 🎯 CLI Commands

```bash
# Status check
kimi-mcp status

# Workflows
kimi-mcp workflow research_to_linear "topic" "team-id"
kimi-mcp workflow bug_fix "KIM-123" "owner/repo"
kimi-mcp workflow competitive_analysis "query" "team-id"
kimi-mcp workflow scraper_build "url" "owner/repo"

# Interactive
kimi-mcp interactive

# With yolo mode
kimi-mcp --yolo workflow research_to_linear "topic" "team-id"
```

## 📈 Architecture

```
┌─────────────────────────────────────────┐
│         KimiMCPClient                   │
│  ┌─────────────────────────────────┐    │
│  │  MCPWorkflows                   │    │
│  │  • research_to_linear           │    │
│  │  • bug_fix                      │    │
│  │  • competitive_analysis         │    │
│  │  • scraper_build                │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │  8 Server Instances             │    │
│  │  • perplexity                   │    │
│  │  • linear                       │    │
│  │  • github                       │    │
│  │  • brave                        │    │
│  │  • firecrawl                    │    │
│  │  • chrome                       │    │
│  │  • playwright                   │    │
│  │  • context7                     │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

## 🧪 Testing

```bash
# Run tests
pytest kimi_mcp_client/

# Test specific server
pytest -k "test_perplexity"
```

## 📝 License

MIT License - See LICENSE file
