# 🚀 MCP Configuration & Automation

> Merged from MCP_SETUP.md and MCP_AUTOMATION_README.md

## Overview

Complete MCP infrastructure with 9 servers and automation tools.

---

## MCP Servers (9 Total)

| Server | Package | Tools | Status | API Key |
|--------|---------|-------|--------|---------|
| 🔥 **firecrawl** | `firecrawl-mcp` | 15+ | ✅ Ready | `~/.env` |
| 🔍 **perplexity** | `@perplexity-ai/mcp-server` | 3 | ✅ Ready | `~/.env` |
| 📋 **linear** | `@linear/mcp` | 42 | ✅ Ready | `~/.env` |
| 🐙 **github** | `@github/mcp-server` | 50+ | ✅ Ready | `~/.env` |
| 🌐 **brave-search** | `@modelcontextprotocol/server-brave-search` | 6 | ✅ Ready | `~/.env` |
| 🛠️ **chrome-devtools** | `@modelcontextprotocol/server-chrome` | 25+ | ✅ Ready | None |
| 🎭 **playwright** | `@executeautomation/playwright-mcp-server` | 10+ | ✅ Ready | None |
| 📚 **context7** | `@upstash/context7-mcp` | 5 | ⏳ Pending | Add to `~/.env` |
| 🧠 **coggraph** | Local Python | 8 | ✅ Ready | None |

**Total: 160+ tools available!**

---

## Quick Start

```bash
# Run full test suite
python mcp_test_suite.py

# Setup Context7
python setup_context7.py --fix-config

# Test browser servers
python test_browser_servers.py

# Run workflow demo
python mcp_workflow_automation.py
```

---

## Server Capabilities

### 🔥 Firecrawl
- **Scrape**: Extract clean markdown from any URL
- **Crawl**: Bulk extract entire websites
- **Search**: Web search with content extraction
- **Map**: Discover all URLs on a site
- **Browser**: Automate browser interactions

### 🔍 Perplexity
- **Ask**: AI-powered Q&A with web grounding
- **Research**: Deep multi-source research
- **Reason**: Step-by-step reasoning with citations

### 📋 Linear
- **Issues**: Create, update, search issues
- **Projects**: Manage project workflows
- **Teams**: View team assignments
- **Cycles**: Sprint planning

### 🐙 GitHub
- **Repos**: Create, fork, search repositories
- **Issues**: Create, update, comment on issues
- **PRs**: Create, review, merge pull requests
- **Code**: Search code, get file contents

### 🌐 Brave Search
- **Web**: Privacy-focused web search
- **News**: Latest news articles
- **Images**: Image search
- **Videos**: Video search

### 🛠️ Chrome DevTools
- **Audit**: Lighthouse performance audits
- **Screenshot**: Capture page screenshots
- **Console**: View browser console logs
- **Network**: Analyze network requests

---

## Workflows

### Research → Linear Issue
```python
from mcp_workflow_automation import MCPWorkflows

result = await MCPWorkflows.research_to_linear(
    topic="React 19 features",
    team_id="your-team-id"
)
```

### Bug Fix Workflow
```python
result = await MCPWorkflows.bug_fix_workflow(
    issue_id="KIM-123",
    repo="owner/repo"
)
```

### Competitive Analysis
```python
result = await MCPWorkflows.competitive_analysis(
    query="AI coding assistants",
    team_id="your-team-id"
)
```

---

## Files

| File | Purpose | Size |
|------|---------|------|
| `mcp_config.json` | MCP server definitions | - |
| `mcp_test_suite.py` | Test all MCP servers | 6.8 KB |
| `setup_context7.py` | Configure Context7 | 3.5 KB |
| `test_browser_servers.py` | Test Chrome & Playwright | 3.8 KB |
| `mcp_workflow_automation.py` | Execution chains | 8.2 KB |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Server not connecting | Check `~/.env` loaded: `echo $FIRECRAWL_API_KEY` |
| Context7 fails | Add API key to `.env` |
| Browser tests fail | Run `npx playwright install` |
| Import errors | Ensure Python 3.8+ installed |

---

**Status**: ✅ Production Ready  
**Tools**: 160+ available
