# Kimi CLI - Optimized Agent Configuration

## Quick Start

```bash
# 1. Set up environment
copy .env.example .env
# Edit .env with your API keys

# 2. Run test
kimi "Research Playwright stealth with Perplexity, scrape HN top 3 headlines with Playwright, create Linear issue"
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Kimi CLI                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │   Kimi K2.5  │  │ 7 MCP Servers│  │ 15 Tools  │  │
│  │  (256k ctx)  │  │              │  │           │  │
│  └──────────────┘  └──────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────┘
```

### MCP Servers (7)

| Server | Use Case | Package |
|--------|----------|---------|
| 🔥 **Firecrawl** | Web scraping, data extraction | `@mendableai/firecrawl-mcp-server` |
| 🔍 **Perplexity** | Research, architecture, docs | `@modelcontextprotocol/server-perplexity` |
| 📋 **Linear** | Issue tracking, task management | `@modelcontextprotocol/server-linear` |
| 🐙 **GitHub** | Code search, PRs, repos | `@modelcontextprotocol/server-github` |
| 🦁 **Brave** | URL discovery, quick search | `@modelcontextprotocol/server-brave-search` |
| 🧪 **Chrome DevTools** | Live DOM debugging | `@modelcontextprotocol/server-puppeteer` |
| 🎭 **Playwright** | Browser automation, anti-bot | `@executeautomation/playwright-mcp-server` |

---

## Tool Routing Rules

### When to Use What

```
RESEARCH     → Perplexity (architecture, docs, factual)
FIND URL     → Brave Search only
EXTRACT DATA → Firecrawl (JSON/markdown, never HTML)
AUTOMATE     → Playwright (headless, anti-bot)
DEBUG LIVE   → Chrome DevTools (active tab)
CODE OPS     → GitHub (search_code first!)
TRACK WORK   → Linear (issues, bugs)
```

### Execution Chains

**SCRAPER BUILD:**
```
1. Brave/Perplexity → Research target
2. Playwright/Firecrawl → Test extraction  
3. Write code → Node/Python
4. GitHub → Push & PR
```

**BUG FIX:**
```
1. Linear → Read issue
2. GitHub → search_code for failing code
3. Write fix
4. GitHub → Create PR
5. Linear → Update ticket
```

---

## Configuration

### Files

| File | Purpose | Size |
|------|---------|------|
| `mcp_config.json` | MCP server definitions | 1.2 KB (env vars) |
| `config.toml` | Kimi CLI settings | 9 KB (7 models) |
| `.env` | API keys (gitignored) | - |

### Environment Variables Required

```bash
# Primary
MOONSHOT_API_KEY=sk-...
KIMI_API_KEY=sk-...

# MCP Servers
FIRECRAWL_API_KEY=fc-...
PERPLEXITY_API_KEY=pplx-...
LINEAR_API_KEY=lin_api_...
GITHUB_TOKEN=ghp_...
BRAVE_API_KEY=BSA...

# Optional providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
DEEPSEEK_API_KEY=...
```

---

## Optimizations Applied

### 1. Token Efficiency
- **System prompt**: 450 chars (was 2000+)
- **Models**: 7 essential (was 30+)
- **Context preservation**: 80% compaction trigger

### 2. Performance
- **Tool timeout**: 45s (was 60s)
- **Max steps**: 50/turn (was 100)
- **Background tasks**: 3 max (was 4)
- **Read bytes**: 20KB max (was 30KB)

### 3. Cost Control
- **Budget ceiling**: $100 (was $200)
- **Warning at**: 70% (was 75%)
- **Alert at**: 85% (was 90%)

### 4. Logging
- **Level**: warn (was info)
- **Max log size**: 5MB (was 10MB)

---

## Available Models

| Model | Provider | Context | Best For |
|-------|----------|---------|----------|
| `kimi-k2-5` | Moonshot | 256k | Default, vision, code |
| `kimi-k2-thinking` | Moonshot | 256k | Deep reasoning |
| `kimi-for-coding` | Kimi Code | 262k | Complex coding tasks |
| `claude-sonnet-4` | Anthropic | 200k | Code review, analysis |
| `gpt-4o` | OpenAI | 128k | General tasks |
| `gemini-2-5-pro` | Google | 1M | Large context, vision |
| `deepseek-reasoner` | DeepSeek | 64k | Math, logic |

---

## Usage Examples

### Web Scraping Pipeline
```bash
kimi "Scrape https://example.com pricing with Firecrawl, 
      handle anti-bot with Playwright if needed, 
      save results to GitHub gist"
```

### Research to Linear
```bash
kimi "Research React 19 features via Perplexity,
      summarize top 5, create Linear issue with findings"
```

### Debug & Fix
```bash
kimi "Read Linear issue SCR-123, find the bug in my repo via GitHub search_code, fix it"
```

---

## Testing

```bash
# Test all 7 MCP servers
kimi "Use Perplexity to check if MCP servers are working, 
      then test Playwright on example.com,
      search for 'playwright-mcp' on GitHub,
      and list my Linear issues"
```

---

## Maintenance

### Update MCP servers
```bash
npx -y @mendableai/firecrawl-mcp-server --version
```

### Check logs
```bash
tail -f ~/.kimi/logs/kimi.log
```

### Reset state
```bash
rm -rf ~/.kimi/state/*
```
