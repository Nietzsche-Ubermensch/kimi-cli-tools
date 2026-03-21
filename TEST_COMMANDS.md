# Testing Kimi CLI Slash Commands

## Quick Test Checklist

### 1. Start Kimi CLI
```bash
cd your-project
kimi
```

### 2. List Available Commands
Type within Kimi CLI:
```
/help
```

You should see the new commands listed:
- `/scrape`, `/get`, `/fetch`
- `/find`, `/search`
- `/docs`, `/doc`, `/man`
- `/explain`, `/what`
- `/refactor`, `/improve`
- `/fix`, `/lint`
- `/test`, `/tests`
- `/github`, `/gh`
- `/status`, `/st`
- `/session`, `/sesh`
- `/config`, `/conf`

### 3. Test Web Commands

**Test /scrape:**
```
/scrape https://example.com
```
Expected: Returns markdown content of the page

**Test /find:**
```
/find python asyncio tutorial
```
Expected: Returns search results

**Test /docs:**
```
/docs python list comprehension
```
Expected: Returns Context7 documentation (requires context7 MCP)

### 4. Test Code Commands

**Test /explain:**
```
/explain kimi_cli/soul/slash.py
```
Expected: Shows file analysis (functions, classes, imports)

**Test /status:**
```
/status
```
Expected: Shows git status and project info

**Test /refactor:**
```
/refactor kimi_cli/soul/builtin_commands.py
```
Expected: Shows refactoring suggestions

### 5. Test Config Commands

**Test /config:**
```
/config list
```
Expected: Shows current configuration

**Test /session:**
```
/session list
```
Expected: Shows saved sessions (or "No saved sessions")

### 6. Test GitHub Command

**Test /github:**
```
/github repo facebook/react
```
Expected: Shows repo info (requires github MCP)

---

## Troubleshooting

### Issue: "Unknown command"
**Cause:** Commands not loaded properly
**Fix:** 
```bash
cd C:\Users\peter\Desktop\Kimi_CLI\kimi-cli
pip install -e .
```

### Issue: "MCP error" or timeout
**Cause:** MCP tools not installed
**Fix:**
```bash
npm install -g @anthropic-ai/mcp-tool
```

### Issue: "Module not found"
**Cause:** Import errors
**Fix:** Check Python syntax:
```bash
cd C:\Users\peter\Desktop\Kimi_CLI\kimi-cli\src
python -m py_compile kimi_cli/soul/slash.py
python -m py_compile kimi_cli/soul/builtin_commands.py
```

---

## Full Command List

| Command | Aliases | Test Command |
|---------|---------|--------------|
| `/scrape` | `/get`, `/fetch` | `/scrape https://example.com` |
| `/find` | `/search` | `/find python asyncio` |
| `/docs` | `/doc`, `/man` | `/docs python list` |
| `/explain` | `/what` | `/explain kimi_cli/soul/slash.py` |
| `/refactor` | `/improve` | `/refactor your_file.py` |
| `/fix` | `/lint` | `/fix your_file.py` |
| `/test` | `/tests` | `/test your_test.py --run` |
| `/github` | `/gh` | `/github repo owner/repo` |
| `/status` | `/st` | `/status --git` |
| `/session` | `/sesh` | `/session list` |
| `/config` | `/conf` | `/config list` |

---

## Success Criteria

✅ All 11 new commands appear in `/help`
✅ `/scrape` returns web content
✅ `/find` returns search results
✅ `/explain` analyzes code files
✅ `/status` shows project info
✅ No import errors in logs
