# MCP Infrastructure Automation

Complete automation suite for the 8-server MCP infrastructure.

## 🚀 Quick Start

```bash
# Run full test suite
python mcp_test_suite.py

# Setup Context7
python setup_context7.py --fix-config
python setup_context7.py --fix-env

# Test browser servers
python test_browser_servers.py

# Run workflow automation demo
python mcp_workflow_automation.py
```

## 📁 Files

| File | Purpose |
|------|---------|
| `mcp_test_suite.py` | Test all 8 MCP servers |
| `setup_context7.py` | Configure Context7 server |
| `test_browser_servers.py` | Test Chrome & Playwright |
| `mcp_workflow_automation.py` | Pre-built execution chains |

## 🔧 Server Status

| Server | Status |
|--------|--------|
| Perplexity | ✅ Operational |
| Linear | ✅ Operational |
| GitHub | ✅ Operational |
| Brave Search | ✅ Operational |
| Firecrawl | ✅ Operational |
| Chrome DevTools | ✅ Ready |
| Playwright | ✅ Ready |
| Context7 | ⚠️ Needs API key |

## 📋 Workflows

- **research_to_linear** - Research → Create issue
- **bug_fix** - Full bug fix with PR
- **competitive_analysis** - Competitor research
- **scraper_build** - Build & deploy scraper

## 🎯 Next Steps

1. Get Context7 API key from https://upstash.com/
2. Run `python mcp_test_suite.py`
3. Enable Linear-GitHub integration
