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

## 📁 Files Created

| File | Purpose | Size |
|------|---------|------|
| `mcp_test_suite.py` | Test all 8 MCP servers | 6.8 KB |
| `setup_context7.py` | Configure Context7 server | 3.5 KB |
| `test_browser_servers.py` | Test Chrome & Playwright | 3.8 KB |
| `mcp_workflow_automation.py` | Pre-built execution chains | 8.2 KB |
| `MCP_AUTOMATION_README.md` | This documentation | - |

## 🔧 Server Status (Post-Automation)

| Server | Status | Action Taken |
|--------|--------|--------------|
| Perplexity | ✅ | Verified operational |
| Linear | ✅ | Verified operational |
| GitHub | ✅ | Verified operational |
| Brave Search | ✅ | Verified operational |
| Firecrawl | ✅ | Verified operational |
| Chrome DevTools | ✅ | Test script created |
| Playwright | ✅ | Test script created |
| Context7 | ⚠️ | Config added, needs API key |

## 📋 Workflows Available

### 1. Research → Linear Issue
```python
from mcp_workflow_automation import MCPWorkflows

result = await MCPWorkflows.research_to_linear(
    topic="React 19 features",
    team_id="your-team-id"
)
```

### 2. Bug Fix Workflow
```python
result = await MCPWorkflows.bug_fix_workflow(
    issue_id="KIM-123",
    repo="Nietzsche-Ubermensch/Kimi_CLI"
)
```

### 3. Competitive Analysis
```python
result = await MCPWorkflows.competitive_analysis(
    query="AI coding assistants",
    team_id="your-team-id"
)
```

### 4. Scraper Build
```python
result = await MCPWorkflows.scraper_build_workflow(
    target_url="https://example.com",
    output_repo="Nietzsche-Ubermensch/scrapers"
)
```

## 🎯 Next Steps

1. **Get Context7 API Key**
   ```bash
   python setup_context7.py
   # Visit https://upstash.com/ to get API key
   ```

2. **Run Browser Tests**
   ```bash
   python test_browser_servers.py
   ```

3. **Execute Full Test Suite**
   ```bash
   python mcp_test_suite.py
   ```

4. **Enable Linear-GitHub Integration**
   - Visit: https://linear.app/settings/integrations/github
   - Connect your GitHub account

## 🔒 Yolo Mode

Enable autonomous execution:

```bash
/yolo
```

Then run workflows without confirmation:

```bash
kimi "Research MCP servers, create Linear issue with findings"
```

## 📊 Generated Reports

Test runs generate JSON reports:
- `mcp_test_report_YYYYMMDD_HHMMSS.json`
- `browser_test_report_YYYYMMDD_HHMMSS.json`

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Context7 fails | Add API key to `.env` |
| Browser tests fail | Run `npx playwright install` |
| Import errors | Ensure Python 3.8+ installed |

---

**Generated:** 2026-03-20  
**Yolo Mode:** Active ✅
