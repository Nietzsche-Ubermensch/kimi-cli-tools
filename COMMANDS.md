# Kimi CLI Slash Commands

Complete reference for all `/` commands.

## Quick Start

```bash
# Install commands
node install.js

# Add to PATH
export PATH="$HOME/.kimi/commands:$PATH"

# View all commands
/help

# Get help for specific command
/help get
```

---

## Web & Content

### `/get` - Retrieve Web Content

Fetch content from URLs with multiple modes.

```bash
# Scrape a single page (default)
/get https://example.com

# Map all URLs on a site
/get --map https://docs.example.com

# Crawl multiple pages
/get --crawl https://blog.example.com --limit=50

# Extract structured data
/get --extract https://example.com/products --prompt="product names and prices"
```

**Modes:**
- `scrape` - Single page content extraction
- `map` - Discover all URLs on a site
- `crawl` - Extract content from multiple linked pages
- `extract` - Structured data extraction using AI

---

### `/search` - Web Search

Search the web with optional content extraction.

```bash
# Basic search
/search "quantum computing breakthroughs"

# Search with results limit
/search "rust async runtime" --limit=20

# Search and scrape top results
/search "AI agents architecture" --scrape
```

**Flags:**
- `--limit=<n>` - Number of results (1-50, default: 10)
- `--scrape` - Fetch full content from top 3 results

---

### `/ask` - AI Q&A (Perplexity)

Ask questions with different reasoning modes.

```bash
# Quick answer (default)
/ask "What is the capital of Australia?"

# Deep research mode
/ask --deep "Explain transformer neural networks"

# Step-by-step reasoning
/ask --reason "If a train leaves at 2 PM..."
```

**Modes:**
- Default - Quick factual answers
- `--deep` - Multi-source research synthesis
- `--reason` - Logical step-by-step analysis

---

## Documentation

### `/docs` - Library Documentation

Query Context7 for programming library documentation.

```bash
# Query React documentation
/docs react useEffect cleanup

# Query Python library
/docs pandas DataFrame merge

# Query Node.js
/docs node.js fs promises
```

**How it works:**
1. Resolves library name to Context7 ID
2. Queries documentation for specific topics
3. Returns relevant code examples and explanations

---

## Reasoning & Execution

### `/think` - Sequential Reasoning

Work through complex problems step by step.

```bash
# Start reasoning chain
/think "Design a caching strategy for high-traffic API"

# Store a thought for later
/think --store cache-strategy "Use Redis with TTL 3600s"

# Recall stored thoughts
/think --recall cache-strategy
```

**Subcommands:**
- Default - Start sequential reasoning session
- `--store <key>` - Save thought to disk
- `--recall <key>` - Retrieve saved thoughts

---

### `/do` - Intent Execution

Execute natural language tasks via the conductor.

```bash
# Execute intent
/do "Create a Linear issue for implementing OAuth"

# Preview execution plan
/do "Deploy to production" --explain

# With context
/do "Refactor auth" --context='{"team":"ENG","priority":"high"}'
```

**Flags:**
- `--explain` - Preview plan without executing
- `--context=<json>` - Additional context (tech stack, constraints)
- `--priority=speed|accuracy|cost` - Optimization mode

---

### `/run` - Workflow Execution

Run predefined workflows (playbooks).

```bash
# List available workflows
/run --list

# Execute workflow
/run deploy-staging

# Resume from step
/run tests --from=3

# Validate without running
/run deploy-prod --dry-run

# With environment variables
/run build --env='{"VERSION":"1.2.3"}'
```

**Flags:**
- `--list` - Show available workflows
- `--from=<step>` - Resume from specific step
- `--env=<json>` - Environment variables
- `--dry-run` - Validate without executing

---

### `/check` - Execution Status

Check status of running or completed executions.

```bash
# Check specific execution
/check exec-abc123

# Wait for completion
/check exec-abc123 --wait

# List recent executions
/check --recent 10
```

**Flags:**
- `--wait` - Block until execution completes
- `--recent=<n>` - Show last n executions

---

## Integrations

### `/gh` - GitHub

GitHub repository management.

```bash
# Issues
/gh issues list owner/repo --state=open --limit=10
/gh issues get 42
/gh issues create "Bug: Login fails" --body="Steps..." --label=bug

# Pull Requests
/gh prs list owner/repo --state=open
/gh prs get 42
/gh prs merge 42 --method=squash

# Repositories
/gh repos list --limit=20
/gh repos get owner/repo

# Branches
/gh branches list owner/repo
/gh branches create owner/repo/feature-x --from=main
```

---

### `/linear` - Linear

Linear project management.

```bash
# Issues
/linear issues list --state=todo --limit=20
/linear issues get ABC-123
/linear issues create "Fix auth bug" --team=ENG --description="Steps..."

# Teams
/linear teams list

# Projects
/linear projects list --limit=10

# Cycles (Sprints)
/linear cycles list
```

---

## Session & Config

### `/session` - Session Management

Bookmark and resume working sessions.

```bash
# Save current session
/session save feature-branch --message="Working on auth"

# Load session (shows info, you cd manually)
/session load feature-branch

# List saved sessions
/session list

# Delete session
/session delete old-session
```

**Stored:**
- Current working directory
- Timestamp
- Optional message

---

### `/config` - Configuration

Manage user preferences.

```bash
# View all config
/config list

# Get/set values
/config get editor
/config set editor vscode
/config set theme dark

# Remove config
/config delete theme
/config reset
```

**Keys:**
- `default_model` - Default AI model
- `editor` - Preferred editor (vscode, vim, etc.)
- `theme` - UI theme preference

---

### `/help` - Help System

```bash
# Show all commands
/help

# Show specific command help
/help get
/help gh
```

---

## Command Comparison

| When you want to... | Use |
|---------------------|-----|
| Fetch a webpage | `/get <url>` |
| Search the web | `/search <query>` |
| Ask a question | `/ask <question>` |
| Look up library docs | `/docs <lib> <query>` |
| Think through a problem | `/think <problem>` |
| Execute a task | `/do <intent>` |
| Run a workflow | `/run <workflow>` |
| Check execution status | `/check <id>` |
| Manage GitHub | `/gh <action>` |
| Manage Linear | `/linear <action>` |
| Save session | `/session save <name>` |
| Change settings | `/config set <key> <value>` |

---

## Installation

```bash
# Run installer
node install.js

# Or manually copy
cp kimi-commands/* ~/.kimi/commands/
cp -r lib ~/.kimi/

# Add to PATH in ~/.bashrc or ~/.zshrc
export PATH="$HOME/.kimi/commands:$PATH"
```
