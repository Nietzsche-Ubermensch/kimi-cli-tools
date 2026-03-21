# Kimi CLI Slash Commands - Complete Reference

> Merged from SLASH_COMMANDS_SUMMARY.md and SLASH_COMMANDS_REFERENCE.md

## Available Commands (19 total)

### Web & Search Commands

| Command | Aliases | Description | Usage | MCP Server |
|---------|---------|-------------|-------|------------|
| `/scrape` | `/get`, `/fetch` | Fetch web content as markdown | `/scrape <url> [--map\|--crawl]` | firecrawl |
| `/find` | `/search` | Web search with results | `/find <query> [--limit=N]` | brave-search / perplexity |
| `/docs` | `/doc`, `/man` | Query library documentation | `/docs <library> <query>` | context7 |

### Code Analysis Commands

| Command | Aliases | Description | Usage |
|---------|---------|-------------|-------|
| `/explain` | `/what` | Analyze code (functions, classes, imports) | `/explain <file> [--symbol=name]` |
| `/refactor` | `/improve` | Suggest code improvements | `/refactor <file> [--apply]` |
| `/fix` | `/lint` | Detect issues (bare except, print, hardcoded secrets) | `/fix <file> [--apply]` |
| `/test` | `/tests` | Check test file existence and framework | `/test <file> [--run\|--generate]` |

### Project & Integration Commands

| Command | Aliases | Description | Usage | MCP Server |
|---------|---------|-------------|-------|------------|
| `/github` | `/gh` | GitHub repo/issue/PR operations | `/github repo <owner/repo>` | github |
| `/status` | `/st` | Project status (git + test framework) | `/status [--git\|--test]` | - |
| `/session` | `/sesh` | Save/load session bookmarks | `/session <save\|load\|list\|delete> [name]` | - |
| `/config` | `/conf` | View/modify config.json | `/config <get\|set\|list> [key] [value]` | - |

### Core Built-in Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `/init` | - | Analyze codebase and generate AGENTS.md |
| `/compact` | - | Compact context to reduce token usage |
| `/clear` | `/reset` | Clear conversation context |
| `/plan` | - | Toggle plan mode (on/off/view/clear) |
| `/yolo` | - | Toggle auto-approval mode |
| `/export` | - | Export session to markdown file |
| `/import` | - | Import context from file or session |
| `/add-dir` | - | Add directory to workspace |

---

## Command Examples

### /scrape
```
/scrape https://example.com          # Fetch single page
/scrape https://example.com --map    # List all URLs on site
/scrape https://example.com --crawl  # Crawl multiple pages
```

### /find
```
/find python asyncio tutorial        # Search web
/find "react hooks" --limit=5        # Limit results
```

### /docs
```
/docs react useEffect                # Look up React useEffect
/docs python list comprehension      # Python docs
```

### /explain
```
/explain src/main.py                 # Analyze file
/explain kimi_cli/soul/slash.py      # Full analysis
```
Output shows:
- Line count
- Function count and names
- Class count and names
- Import statements

### /refactor
```
/refactor myfile.py                  # Show suggestions
/refactor myfile.py --apply          # Auto-apply fixes
```
Detects:
- Bare except clauses
- print() statements (should use logging)
- Hardcoded passwords/secrets
- Long files (>300 lines)

### /fix
```
/fix myfile.py                       # List issues
/fix myfile.py --apply               # Apply fixes
```

### /status
```
/status                              # Full status
/status --git                        # Git only
/status --test                       # Test framework only
```
Shows:
- Git branch and uncommitted changes
- Test framework (pytest, jest, etc.)
- Project type (Python, Node.js)

### /session
```
/session save myproject              # Bookmark current dir
/session load myproject              # Show saved dir
/session list                        # List all sessions
/session delete myproject            # Remove session
```

### /config
```
/config list                         # Show all config
/config get api_key                  # Get value
/config set theme dark               # Set value
/config delete theme                 # Remove key
```

### /github
```
/github repo facebook/react          # Search repo
/github issue 123                    # Get issue
/github pr 456                       # Get PR
```

---

## Architecture

### Implementation Files

| File | Description |
|------|-------------|
| `kimi-cli/src/kimi_cli/soul/builtin_commands.py` | 11 new command classes |
| `kimi-cli/src/kimi_cli/soul/slash.py` | Command registrations |

### Class Hierarchy
```
SlashCommand (base)
  ├── WebCommand (adds call_mcp helper)
  │     ├── ScrapeCommand
  │     ├── FindCommand
  │     ├── DocsCommand
  │     └── GithubCommand
  ├── ExplainCommand
  ├── RefactorCommand
  ├── FixCommand
  ├── TestCommand
  ├── StatusCommand
  ├── SessionCommand
  └── ConfigCommand
```

### Execution Flow
```
User: /scrape https://example.com
  ↓
slash.py:scrape() handler
  ↓
execute_command("scrape", args, soul)
  ↓
ScrapeCommand.execute(args, soul)
  ↓
WebCommand.call_mcp("firecrawl-mcp", "firecrawl_scrape", params)
  ↓
npx @anthropic-ai/mcp-tool firecrawl-mcp firecrawl_scrape --input {...}
  ↓
Return CommandResult → wire_send(TextPart(text=result.output))
```

---

## Configuration

### Files

| File | Purpose |
|------|---------|
| `~/.env` | API keys (KIMI_API_KEY, MOONSHOT_API_KEY, etc.) |
| `~/.kimi/mcp.json` | MCP server configurations |
| `~/.kimi/config.json` | User config (set via /config) |
| `~/.kimi/sessions/` | Session bookmarks |

### MCP Servers (9)

All configured in `~/.kimi/mcp.json`:

1. **firecrawl** - Web scraping, search, crawling
2. **brave-search** - Web search API
3. **perplexity** - AI-powered search
4. **context7** - Technical documentation
5. **github** - GitHub API access
6. **linear** - Issue tracking
7. **chrome-devtools** - Browser automation
8. **coggraph** - Cognitive graphs
9. **conductor** - Workflow orchestration

---

## Testing

### Syntax Check
```bash
cd kimi-cli/src
python -m py_compile kimi_cli/soul/slash.py
python -m py_compile kimi_cli/soul/builtin_commands.py
```

### Integration Test
```bash
# From within Kimi CLI, try:
/help                    # Should show new commands
/scrape https://example.com  # Should fetch content
/find python async      # Should search web
/explain kimi_cli/soul/slash.py  # Should analyze file
/status                  # Should show git status
```

---

**Status**: ✅ Production Ready  
**Total Commands**: 19 (11 new + 8 existing)
