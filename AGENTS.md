# Kimi CLI Tools - Agent Guide

This document provides essential context for AI agents working on the Kimi CLI Tools project.

## Project Overview

**Kimi CLI Tools** is a full-featured MCP (Model Context Protocol) client with 8 servers, a thermodynamic execution framework, and production-ready orchestration.

- **Repository**: https://github.com/Nietzsche-Ubermensch/kimi-cli-tools
- **Primary Package**: `kimi_mcp_client/`
- **Language**: Python 3.11+
- **License**: MIT

### Core Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Kimi CLI Tools                               │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐    ┌──────────────────┐                       │
│  │ KimiMCPClient    │    │ Thermo Framework │                       │
│  │ (8 MCP Servers)  │    │ (T* Formula)     │                       │
│  └──────────────────┘    └──────────────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Core Language | Python 3.11+ | Main implementation |
| HTTP Client | aiohttp | Async API calls |
| Data Validation | pydantic | Type checking |
| CLI Framework | argparse | Command-line interface |
| Environment | python-dotenv | Configuration management |
| Testing | pytest, pytest-asyncio | Unit tests |

## Project Structure

```
C:\Users\peter\Desktop\Kimi_CLI/
├── kimi_mcp_client/              # Main Python package
│   ├── __init__.py               # Package exports
│   ├── client.py                 # KimiMCPClient orchestrator
│   ├── cli.py                    # Command-line interface
│   ├── workflows.py              # Pre-built execution chains
│   ├── integration_gateway.py    # External API gateway
│   ├── servers/                  # Server implementations
│   │   ├── __init__.py           # Server exports
│   │   ├── base.py               # BaseMCPServer (abstract base)
│   │   ├── perplexity.py         # Perplexity API wrapper
│   │   ├── linear.py             # Linear GraphQL API
│   │   ├── github.py             # GitHub REST API
│   │   ├── brave.py              # Brave Search API
│   │   ├── firecrawl.py          # Firecrawl REST API
│   │   ├── chrome.py             # Chrome DevTools stub
│   │   ├── playwright.py         # Playwright stub
│   │   └── context7.py           # Context7 API (optional)
│   ├── agents/                   # Agent implementations
│   │   ├── __init__.py
│   │   └── research_agent.py     # Research orchestrator
│   ├── soul/                     # LaborMarket agents
│   │   └── agent.py              # SubAgent implementation
│   ├── tools/                    # Utility tools
│   │   ├── __init__.py
│   │   ├── code_analyzer.py      # Code analysis
│   │   └── file_operations.py    # File manager
│   ├── requirements.txt          # Package dependencies
│   ├── setup.py                  # Package setup
│   └── README.md                 # Package documentation
│
├── kimi_thermo/                  # Thermodynamic framework (standalone)
│   ├── __init__.py
│   ├── thermo_executor.py        # Core T* implementation
│   ├── dynamic_complete.py       # Dynamic client
│   ├── complete_cli.py           # CLI with audit dashboard
│   ├── tools_complete.py         # Tool registry
│   └── main.py                   # Entry point
│
├── .kimi/skills/                 # Skill patterns
│   ├── kimi-thermodynamic/       # T* framework skill
│   ├── firecrawl-*/              # Firecrawl skills
│   ├── python-async-mcp/         # MCP client skill
│   └── ...
│
├── config.toml                   # Kimi CLI configuration
├── mcp_config.json               # MCP server configurations
├── pyproject.toml                # Project metadata
├── .env.example                  # Environment template
├── demo_full_implementation.py   # Usage examples
└── test_*.py                     # Test files
```

## MCP Server Architecture

### 8 MCP Servers

| Server | Status | Backend | Key Tools |
|--------|--------|---------|-----------|
| **Firecrawl** | ✅ Working | Firecrawl REST API | `scrape`, `crawl`, `extract`, `map`, `search` |
| **Perplexity** | ✅ Working | Perplexity REST API | `ask`, `research`, `reason` |
| **Linear** | ✅ Working | Linear GraphQL API | `create_issue`, `update_issue`, `get_teams` |
| **GitHub** | ✅ Working | GitHub REST API | `search_code`, `create_pr`, `push_files` |
| **Brave** | ✅ Working | Brave Search API | `web_search`, `image_search`, `news_search` |
| **Context7** | ⚠️ Optional | Context7/Upstash API | `resolve_library`, `query_docs` |
| **Chrome** | ⚠️ Stub | Firecrawl browser* | DevTools stub (use Firecrawl instead) |
| **Playwright** | ⚠️ Stub | Requires MCP server* | Testing stub (requires npx server) |

*For full browser automation, use Firecrawl's browser features.

### Server Base Class Pattern

All servers inherit from `BaseMCPServer` and use `aiohttp` for HTTP requests:

```python
class ExampleServer(BaseMCPServer):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("env", {}).get("API_KEY") or os.environ.get("API_KEY")
        self.base_url = "https://api.example.com"
    
    async def health_check(self) -> Dict[str, Any]:
        # Verify API access
        pass
    
    async def some_method(self, param: str) -> Dict[str, Any]:
        self._track_request()
        session = await self._get_session()
        async with session.get(...) as resp:
            return await resp.json()
```

## Build and Test Commands

### Installation

```bash
# Install the full client package
pip install -e kimi_mcp_client/

# Install with dev dependencies
pip install -e "kimi_mcp_client/[dev]"
```

### Running Tests

```bash
# Run all tests
pytest kimi_mcp_client/

# Test specific server
pytest -k "test_perplexity"

# Run with verbose output
pytest -v

# Run async tests
pytest --asyncio-mode=auto
```

### Test Files

| File | Purpose |
|------|---------|
| `test_kimi_cli.py` | CLI integration tests |
| `test_services.py` | Live API service tests |
| `test_browser_servers.py` | Browser automation tests |
| `test_openrouter_debug.py` | OpenRouter debugging |

### Manual Testing

```bash
# Test service connectivity
python test_services.py

# Test CLI with live commands
python test_kimi_cli.py

# Run full demo
python demo_full_implementation.py
```

## Code Style Guidelines

### Python Conventions

1. **Type Hints**: Use type hints for function parameters and return values
   ```python
   async def scrape(self, url: str, formats: List[str] = None) -> Dict[str, Any]:
   ```

2. **Docstrings**: Use Google-style docstrings
   ```python
   """
   Scrape a single page.
   
   Args:
       url: Page URL to scrape
       formats: Output formats [markdown, html, json]
       
   Returns:
       Scraped content in requested formats
   """
   ```

3. **Async/Await**: All API calls must use async/await patterns
   ```python
   async def health_check(self) -> Dict[str, Any]:
       session = await self._get_session()
       async with session.get(...) as resp:
           return await resp.json()
   ```

4. **Naming Conventions**:
   - Classes: `PascalCase` (e.g., `FirecrawlServer`)
   - Functions/Variables: `snake_case` (e.g., `health_check`)
   - Constants: `UPPER_CASE` (e.g., `BUDGET_CAP`)
   - Private: `_leading_underscore` (e.g., `_track_request`)

### File Organization

- One class per file for server implementations
- Group related functionality in subdirectories
- Keep `__init__.py` files updated with exports

## Configuration

### Environment Variables (`.env`)

Required API keys (copy from `.env.example`):

```bash
# ─── PRIMARY API KEYS ────────────────────────────────────────────────────────
MOONSHOT_API_KEY=sk-...
KIMI_API_KEY=sk-...

# ─── MCP SERVER API KEYS ─────────────────────────────────────────────────────
FIRECRAWL_API_KEY=fc-...
PERPLEXITY_API_KEY=pplx-...
LINEAR_API_KEY=lin_api_...
GITHUB_TOKEN=ghp_...
BRAVE_API_KEY=BSA...

# ─── OPTIONAL PROVIDERS ──────────────────────────────────────────────────────
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
DEEPSEEK_API_KEY=...
VENICE_API_KEY=...
ZHIPU_API_KEY=...
MODELSCOPE_API_KEY=...
NSCALE_API_KEY=...
```

### MCP Config (`mcp_config.json`)

Server configurations for stdio MCP server mode:

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "@mendableai/firecrawl-mcp-server"],
      "env": {"FIRECRAWL_API_KEY": "..."}
    },
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-perplexity"],
      "env": {"PERPLEXITY_API_KEY": "..."}
    }
  }
}
```

## CLI Usage

### Commands

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

### Available Workflows

| Workflow | Description | Arguments |
|----------|-------------|-----------|
| `research_to_linear` | Research → Create Linear Issue | `<topic> <team_id>` |
| `bug_fix` | Bug fix with PR | `<issue_id> <repo>` |
| `competitive_analysis` | Competitor research | `<query> <team_id>` |
| `scraper_build` | Build and deploy scraper | `<url> <repo>` |
| `documentation_lookup` | Library docs search | `<library> <question>` |

## Python API Usage

```python
import asyncio
from kimi_mcp_client import KimiMCPClient

async def main():
    client = KimiMCPClient(yolo_mode=True)
    
    # Initialize all servers
    status = await client.initialize()
    print(status)
    
    # Use Firecrawl for web scraping
    result = await client.firecrawl.scrape(
        url="https://example.com",
        formats=["markdown"]
    )
    
    # Use Perplexity for research
    answer = await client.perplexity.ask("What is MCP?")
    
    # Use GitHub for code operations
    issues = await client.github.list_issues("owner", "repo")
    
    # Use Linear for issue tracking
    teams = await client.linear.get_teams()
    
    # Run pre-built workflow
    result = await client.workflows.research_to_linear(
        topic="React 19 features",
        team_id="your-team-id"
    )
    
    # Close client
    await client.close()

asyncio.run(main())
```

## Thermodynamic Framework

T* formula: `(L - γ) / (|L| + λ)`

- **L** = Confidence (0-1)
- **γ** = Risk penalty (0-1)
- **λ** = Smoothing factor (0.1)

Regimes:
- **ACT** (T* > 0.3): Execute normally
- **HOLD** (-0.3 < T* ≤ 0.3): Ground with search
- **REFUSE** (T* ≤ -0.3): Reject query

### Thermo CLI Commands

```bash
# Run with audit dashboard
python -m kimi_thermo.complete_cli --audit

# Get JSON audit
python -m kimi_thermo.complete_cli --audit-json

# List all tools
python -m kimi_thermo.complete_cli --tools

# Execute query
python -m kimi_thermo.complete_cli "your query"
```

## Testing Instructions

### Unit Tests

Create tests using pytest:

```python
import pytest
from kimi_mcp_client.servers import FirecrawlServer

@pytest.mark.asyncio
async def test_firecrawl_scrape():
    server = FirecrawlServer({"env": {"FIRECRAWL_API_KEY": "test"}})
    result = await server.health_check()
    assert result["status"] in ["healthy", "error"]
```

### Integration Tests

Test with real API calls (requires valid API keys):

```python
# test_services.py pattern
async def test_firecrawl():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://api.firecrawl.dev/v1/scrape',
            headers={'Authorization': f'Bearer {os.environ.get("FIRECRAWL_API_KEY")}'},
            json={'url': 'https://example.com', 'formats': ['markdown']}
        ) as resp:
            data = await resp.json()
            assert data.get('success')
```

## Security Considerations

### Critical Rules

1. **Never commit `.env`**: The `.env` file is gitignored for security
2. **API key rotation**: Regularly rotate API keys in production
3. **Token masking**: Logs should mask API keys (show only first 8 chars)
4. **GitHub push protection**: Enabled to prevent accidental secret commits

### Environment Security

```python
# Correct - load from environment
import os
api_key = os.environ.get("FIRECRAWL_API_KEY")

# Incorrect - hardcoded
api_key = "fc-abc123..."
```

### Yolo Mode Warning

The `yolo_mode` flag bypasses confirmations. Use carefully:

```python
# Safe - confirmations enabled
client = KimiMCPClient(yolo_mode=False)

# Risky - no confirmations (destructive ops)
client = KimiMCPClient(yolo_mode=True)
```

## Adding a New Server

1. Create `kimi_mcp_client/servers/<name>.py`:
   ```python
   from .base import BaseMCPServer
   
   class NewServer(BaseMCPServer):
       async def health_check(self) -> Dict[str, Any]:
           pass
   ```

2. Add to `kimi_mcp_client/servers/__init__.py`:
   ```python
   from .new import NewServer
   ```

3. Register in `kimi_mcp_client/client.py` `_server_registry()`:
   ```python
   def _server_registry(self) -> Dict[str, Any]:
       return {
           ...
           "new": NewServer,
       }
   ```

4. Add property accessor in `KimiMCPClient`:
   ```python
   @property
   def new(self) -> NewServer:
       return self._servers.get("new")
   ```

5. Add to `kimi_mcp_client/__init__.py` exports

## Troubleshooting

### Server Connection Issues

If servers show "error" status:

1. **Check API keys** in `.env` file
2. **Verify network** - can you reach the APIs?
3. **Check key names** - must match the server's expected env vars
4. **Test individually**:
   ```python
   from kimi_mcp_client.servers import FirecrawlServer
   server = FirecrawlServer({"env": {"FIRECRAWL_API_KEY": "your-key"}})
   print(await server.health_check())
   ```

### Browser Automation Workaround

Since Chrome/Playwright are stubs, use Firecrawl:

```python
# Instead of chrome.navigate() + chrome.screenshot()
result = await client.firecrawl.scrape(
    url="https://example.com",
    formats=["markdown", "screenshot"],
    wait_for=5000  # Wait for JS rendering
)
```

## Key Files for Agents

| File | Purpose |
|------|---------|
| `kimi_mcp_client/client.py` | Main client implementation |
| `kimi_mcp_client/workflows.py` | Workflow definitions |
| `kimi_mcp_client/servers/base.py` | Base server class |
| `kimi_mcp_client/servers/*.py` | Individual server implementations |
| `kimi_thermo/thermo_executor.py` | Thermodynamic framework |
| `config.toml` | System prompts and tool configurations |
| `mcp_config.json` | MCP server configurations |
| `demo_full_implementation.py` | Usage examples |

---

*Last updated: 2026-03-25*
