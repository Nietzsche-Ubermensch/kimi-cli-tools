# Kimi CLI Tools

Async Python MCP client with 7 servers, thermodynamic execution framework, and optimized configurations.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/Nietzsche-Ubermensch/kimi-cli-tools.git
cd kimi-cli-tools
cp .env.example .env
# Edit .env with your API keys

# Install dependencies
pip install -e .

# Run
kimi "Your query here"
```

## 📦 What's Included

### 7 MCP Servers
| Server | Purpose | Package |
|--------|---------|---------|
| 🔥 Firecrawl | Web scraping | `@mendableai/firecrawl-mcp-server` |
| 🔍 Perplexity | Research | `@modelcontextprotocol/server-perplexity` |
| 📋 Linear | Issue tracking | `@modelcontextprotocol/server-linear` |
| 🐙 GitHub | Code operations | `@modelcontextprotocol/server-github` |
| 🦁 Brave | Search | `@modelcontextprotocol/server-brave-search` |
| 🧪 Chrome DevTools | Live debugging | `@modelcontextprotocol/server-puppeteer` |
| 🎭 Playwright | Browser automation | `@executeautomation/playwright-mcp-server` |

### Key Files
- `mcp_config.json` - MCP server configuration
- `config.toml` - Kimi CLI settings with tool routing rules
- `kimi_full_client.py` - Main async client with fiber execution
- `kimi_thermo/` - Thermodynamic execution framework (T*)
- `.kimi/skills/` - Generated skill documentation
- `AGENTS.md` - Project guide for AI agents

## 🔧 Configuration

### Environment Variables
Create `.env` from `.env.example`:
```bash
MOONSHOT_API_KEY=sk-...
KIMI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
PERPLEXITY_API_KEY=pplx-...
LINEAR_API_KEY=lin_api_...
GITHUB_TOKEN=ghp_...
BRAVE_API_KEY=BSA...
```

### Tool Routing Rules
```
RESEARCH      → Perplexity
FIND URL      → Brave
EXTRACT DATA  → Firecrawl (JSON/markdown)
AUTOMATE      → Playwright
DEBUG LIVE    → Chrome DevTools
CODE OPS      → GitHub (search_code first!)
TRACK WORK    → Linear
```

## 🧠 Thermodynamic Framework

T* formula: `(L - γ) / (|L| + λ)`

- **ACT** (T* > 0): Execute normally
- **HOLD** (-1 < T* ≤ 0): Auto-ground with search
- **REFUSE** (T* ≤ -1): Reject query

## 📚 Documentation

- [AGENTS.md](AGENTS.md) - Full project documentation
- [.kimi/skills/](.kimi/skills/) - Skill patterns for AI

## 🔒 Security

- `.env` is gitignored - never commit secrets
- `MCP_SETUP.md` and `QUICK_START.md` excluded (contained exposed keys)
- GitHub push protection enabled

## 📄 License

MIT
