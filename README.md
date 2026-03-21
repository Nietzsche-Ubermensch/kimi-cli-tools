# Kimi CLI Tools

Full-featured MCP client with 8 servers, thermodynamic execution framework, and production-ready orchestration.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/Nietzsche-Ubermensch/kimi-cli-tools.git
cd kimi-cli-tools
cp .env.example .env
# Edit .env with your API keys

# Install the full client
pip install -e kimi_mcp_client/

# Run CLI
kimi-mcp status          # Check all 8 servers
kimi-mcp interactive     # Start interactive mode
```

## 📦 Two Implementations

### 1. **Full Client Package** (`kimi_mcp_client/`)
Production-ready async client with all 8 servers:

```python
from kimi_mcp_client import KimiMCPClient

client = KimiMCPClient(yolo_mode=True)
await client.initialize()

# Direct server access
answer = await client.perplexity.ask("What is MCP?")
issue = await client.linear.create_issue(title="New feature")
code = await client.github.search_code(query="repo:owner/repo")

# Pre-built workflows
result = await client.workflows.research_to_linear(
    topic="React 19 features",
    team_id="your-team-id"
)
```

### 2. **Legacy Files**
- `kimi_full_client.py` - Original prototype
- `kimi_thermo/` - Standalone thermodynamic framework

## 🔌 8 MCP Servers

| Server | Purpose | Key Tools |
|--------|---------|-----------|
| 🔥 **Firecrawl** | Web scraping | `scrape`, `crawl`, `extract` |
| 🔍 **Perplexity** | Research & Q&A | `ask`, `research`, `reason` |
| 📋 **Linear** | Issue tracking | `create_issue`, `update_issue` |
| 🐙 **GitHub** | Code operations | `search_code`, `create_pr`, `push_files` |
| 🦁 **Brave** | Web search | `web_search`, `image_search` |
| 🧪 **Chrome DevTools** | Live debugging | `navigate`, `screenshot`, `snapshot` |
| 🎭 **Playwright** | Cross-browser testing | `new_page`, `goto`, `expect` |
| 📚 **Context7** | Documentation lookup | `resolve_library`, `query_docs` |

## 🔄 Pre-Built Workflows

```bash
# Research → Linear Issue
kimi-mcp workflow research_to_linear "React 19 features" "team-id"

# Bug Fix with PR
kimi-mcp workflow bug_fix "KIM-123" "owner/repo"

# Competitive Analysis
kimi-mcp workflow competitive_analysis "AI coding assistants" "team-id"

# Build Scraper
kimi-mcp workflow scraper_build "https://example.com" "owner/repo"
```

## 🔧 Configuration

### Environment Variables (`.env`)
```bash
MOONSHOT_API_KEY=sk-...
KIMI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
PERPLEXITY_API_KEY=pplx-...
LINEAR_API_KEY=lin_api_...
GITHUB_TOKEN=ghp_...
BRAVE_API_KEY=BSA...
CONTEXT7_API_KEY=...       # Optional
```

### MCP Config (`mcp_config.json`)
All 8 servers configured via npx:
```json
{
  "mcpServers": {
    "perplexity": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-perplexity"]},
    "linear": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-linear"]},
    "github": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]},
    "brave": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-brave-search"]},
    "firecrawl": {"command": "npx", "args": ["-y", "@mendableai/firecrawl-mcp-server"]},
    "chrome": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-puppeteer"]},
    "playwright": {"command": "npx", "args": ["-y", "@executeautomation/playwright-mcp-server"]},
    "context7": {"command": "npx", "args": ["-y", "@upstash/context7-mcp"]}
  }
}
```

## 🛠️ Package Structure

```
kimi_mcp_client/
├── __init__.py          # Package exports
├── client.py            # KimiMCPClient orchestrator
├── cli.py               # Command-line interface
├── workflows.py         # Execution chains
├── servers/             # Server implementations
│   ├── base.py          # BaseMCPServer
│   ├── perplexity.py    # Research
│   ├── linear.py        # Issues
│   ├── github.py        # Code
│   ├── brave.py         # Search
│   ├── firecrawl.py     # Scraping
│   ├── chrome.py        # DevTools
│   ├── playwright.py    # Testing
│   └── context7.py      # Docs
├── requirements.txt
├── setup.py
└── README.md
```

## 🧠 Thermodynamic Framework

T* formula: `(L - γ) / (|L| + λ)`

- **L** = Confidence (0-1)
- **γ** = Risk penalty (0-1)
- **λ** = Smoothing factor (0.1)

Regimes:
- **ACT** (T* > 0.3): Execute normally
- **HOLD** (-0.3 < T* ≤ 0.3): Ground with search
- **REFUSE** (T* ≤ -0.3): Reject query

## 📚 Documentation

- [AGENTS.md](AGENTS.md) - Project guide for AI agents
- [kimi_mcp_client/README.md](kimi_mcp_client/README.md) - Full package docs
- [demo_full_implementation.py](demo_full_implementation.py) - Usage examples
- `.kimi/skills/` - Skill patterns

## 🎯 CLI Commands

```bash
# Check all servers
kimi-mcp status

# Run workflow
kimi-mcp workflow research_to_linear "topic" "team-id"

# Interactive mode
kimi-mcp interactive

# With yolo mode (no confirmations)
kimi-mcp --yolo workflow bug_fix "KIM-123" "owner/repo"
```

## 🔒 Security

- `.env` is gitignored - never commit secrets
- GitHub push protection enabled
- API keys loaded from environment

## 📄 License

MIT License - See LICENSE file
