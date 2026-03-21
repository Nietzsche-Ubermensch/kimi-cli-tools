# Kimi K2.5 Quick Start Guide

**Status:** ✓ Fully configured and ready to use
**Date:** 2026-03-16

## 🚀 One-Command Quick Start

### Kimi CLI
```bash
kimi                           # Interactive mode
kimi exec "git status"         # Direct execution
kimi --audit                   # Check usage/costs
```

### OpenClaw + Kimi K2.5
```bash
openclaw models list           # Verify models loaded
openclaw agent --help          # Agent commands
```

### Python API (when Python is fixed)
```bash
cd ~/.kimi/examples
python streaming_tool_calls.py
```

## 🎯 What You Have

### Models (5 registered in OpenClaw)

| Model | Context | Capabilities | Best For |
|---|---|---|---|
| **kimi-k2.5** ⭐ | 256k | text+image, reasoning | Vision tasks, complex analysis |
| kimi-k2-thinking-turbo | 256k | reasoning, fast | Production (paid users) |
| kimi-k2-thinking | 256k | reasoning, deep | Extended reasoning tasks |
| kimi-k2-turbo-preview | 256k | text | Fast responses |
| kimi-k2-0905-preview | 256k | text | Standard tasks |

### Tools (13 Moonshot Formula Tools)

Built into Kimi CLI:

| Tool | Purpose | Cost |
|---|---|---|
| web_search | Real-time search | $0.02 |
| fetch | URL → Markdown | $0.01 |
| code_runner | Python execution | $0.01 |
| quickjs | JavaScript execution | $0.01 |
| excel | Spreadsheet analysis | $0.01 |
| memory | Persistent storage | $0.005 |
| convert | Unit conversions | $0.001 |
| rethink | Planning/reasoning | $0.001 |

### Configuration Files

```
~/.kimi/
├── config.toml          # Kimi CLI settings
├── SETUP.md            # Installation guide
├── QUICK_START.md      # This file
└── examples/
    ├── streaming_tool_calls.py
    └── README.md

~/.openclaw/
├── openclaw.json       # OpenClaw + Moonshot config
└── SETUP_COMPLETE.md   # Full setup docs

~/
├── AGENTS.md           # Agent steering for Kimi K2.5
└── HEARTBEAT.md        # Autonomous monitoring

~/.env                  # API keys (MOONSHOT_API_KEY)
~/.bashrc_github        # Auto-load env vars
```

## 💡 Common Tasks

### 1. Interactive Chat
```bash
kimi
kimi> How do I use web search?
kimi> /tools                 # List available tools
kimi> /shell                 # Enter shell mode
kimi> /think on              # Enable thinking mode
```

### 2. Execute Shell Commands via Kimi
```bash
kimi exec "ls -la"
kimi exec "git status"
kimi exec "npm run build"
```

### 3. Python API (Streaming + Tools)
```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.ai/v1"
)

stream = client.chat.completions.create(
    model="kimi-k2-thinking-turbo",
    messages=[{"role": "user", "content": "Hello Kimi!"}],
    stream=True,
    extra_body={"thinking": {"type": "enabled"}}
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 4. Vision Analysis (Kimi K2.5)
```python
# When Python is working
response = client.chat.completions.create(
    model="kimi-k2.5",  # Only K2.5 has vision
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image"},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
        ]
    }]
)
```

### 5. OpenClaw Agent
```bash
# Check available commands
openclaw --help

# Run agent
openclaw agent --model moonshot/kimi-k2-thinking-turbo

# Security audit
openclaw security audit --deep
```

## 🔑 Your API Key

**Location:** `~/.env`, `~/.openclaw/openclaw.json`, `~/.kimi/config.toml`

```bash
MOONSHOT_API_KEY=sk-kimi-ZufGjPWCzFQTjGSXmtgdZ82Drnytnd0qPEBitLINhfStIVGRhfzf0iK5kG2o6TDU
```

Auto-loaded via `~/.bashrc_github` on shell start.

## 🐛 Known Issues

### Python Broken
**Problem:** `Fatal Python error: Failed to import encodings module`
**Cause:** Microsoft Store Python installation
**Fix:** Uninstall Microsoft Store version, install from python.org
**Status:** Pending user action

### OpenClaw on Windows
**Note:** OpenClaw recommends WSL2 for best experience
**Current:** Running natively on Windows (may have limitations)
**Workaround:** Use via Git Bash (working)

## 📚 Documentation

### Local Files
- **Full setup:** `~/.openclaw/SETUP_COMPLETE.md`
- **Kimi CLI:** `~/.kimi/SETUP.md`
- **Examples:** `~/.kimi/examples/README.md`
- **Agent config:** `~/AGENTS.md`

### Online Resources
- **Moonshot Platform:** https://platform.moonshot.ai
- **OpenClaw Docs:** https://docs.openclaw.ai
- **API Reference:** https://platform.moonshot.ai/docs

### Help Commands
```bash
kimi --help
kimi --version
openclaw --help
openclaw models list
```

## 🎨 Example Workflows

### Workflow 1: Code Review with Tools
```bash
kimi
kimi> Use web_search to find latest TypeScript best practices
kimi> Use code_runner to check if this code has type errors
kimi> Use rethink to plan refactoring approach
```

### Workflow 2: Data Analysis
```bash
kimi
kimi> Use excel tool to analyze sales_data.xlsx
kimi> Use convert to normalize units
kimi> Generate summary report
```

### Workflow 3: Autonomous Monitoring (Heartbeat)
```bash
# Set up cron (future)
*/15 * * * * cd ~/GitHub/ai-suite && openclaw heartbeat
```

## ⚡ Performance Tips

1. **Use thinking mode for complex tasks:**
   ```bash
   kimi> /think on
   ```

2. **Choose the right model:**
   - Vision? → kimi-k2.5
   - Speed? → kimi-k2-turbo-preview
   - Deep reasoning? → kimi-k2-thinking
   - Production? → kimi-k2-thinking-turbo

3. **Monitor costs:**
   ```bash
   kimi --audit
   ```

4. **Stream for better UX:**
   ```python
   stream=True  # In Python API
   ```

## 🔗 Integration Points

### With Claude Code
- Both use YOLO mode (no confirmations)
- Shared GitHub MCP server
- Combined workflow possible

### With GitHub
- `gh` CLI authenticated
- Auto-commit via `/github-yolo`
- PR creation automated

### With Existing Projects
- AI Suite: React + Express
- Document Signing: Post-quantum crypto
- Multimodal AI: GitHub Actions

## 🆘 Troubleshooting

**Kimi CLI not found:**
```bash
which kimi  # Should show path
npm list -g kimi-code-cli
```

**OpenClaw not found:**
```bash
which openclaw  # Should show path
npm list -g openclaw
```

**API key not loaded:**
```bash
echo $MOONSHOT_API_KEY
source ~/.bashrc_github  # Reload
```

**Models not showing:**
```bash
openclaw models list | grep kimi
cat ~/.openclaw/openclaw.json | grep kimi
```

---

## Next Steps

1. ✓ Setup complete
2. ✓ Models registered
3. ✓ Examples created
4. ⏳ Fix Python (reinstall from python.org)
5. ⏳ Test streaming example
6. ⏳ Set up Heartbeat automation (optional)

**Ready to use!** Start with `kimi` for interactive mode or check the examples in `~/.kimi/examples/`.
