# MCP Server Architecture

## Overview
The Kimi MCP client uses a modular, config-driven architecture based on the Model Context Protocol (MCP). It integrates the implemented server set (`firecrawl`, `perplexity`, `linear`, `github`, `brave`, `chrome`, `playwright`, `context7`) through a unified Python interface.

Servers are defined externally (via npx or Python) and orchestrated by the client.

## Core Components

### 1. Configuration (`mcp_config.json`)
- Central JSON file defining all MCP servers.
- Structure:
  ```json
  {
    "mcpServers": {
      "firecrawl": {
        "command": "npx",
        "args": ["-y", "@mendableai/firecrawl-mcp-server"],
        "env": { "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}" }
      },
      "brave-search": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
      },
      "chrome-devtools": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
      },
      "fetch": {
        "type": "streamable_http",
        "url": "${MODELSCOPE_MCP_URL}",
        "headers": { "Authorization": "Bearer ${MODELSCOPE_API_KEY}" }
      }
    }
  }
  ```
- The repository config uses `${VAR}` placeholders, and the Python client does not resolve them; resolve placeholders via external tooling or manual replacement before `client.initialize()`.
- Current key mapping differences:
  - Config key `brave-search` maps to in-process client server key `brave`.
  - Config key `chrome-devtools` maps to in-process client server key `chrome`.
  - Config key `fetch` is included to mirror the current `mcp_config.json`, but only keys defined in `KimiMCPClient._server_registry()` are initialized by the Python client today.
- Easy to extend by adding new server entries.

### 2. KimiMCPClient (client.py)
- Main orchestrator class.
- Loads config and manages server lifecycle.
- Provides dot-notation access: `client.linear.create_issue(...)`
- Key methods:
  - `initialize()`: Loads config and starts servers.
  - Lazy server instantiation via `_server_registry()`.
  - `execute_chain()` for sequential async operations.
  - Workflows via `client.workflows`.

### 3. BaseMCPServer (servers/base.py)
- Abstract base class for all servers.
- Responsibilities:
  - Config storage
  - Per-server shared `aiohttp.ClientSession` management (lazy, with timeout)
  - Request metrics (`request_count`, `last_used`)
  - Abstract `health_check()` method (must be implemented by subclasses)
  - Resource cleanup via `close()`

### 4. Specific Server Implementations (servers/*.py)
- Each server (e.g., `LinearServer`, `GitHubServer`, `FirecrawlServer`) inherits from `BaseMCPServer`.
- Implements `health_check()`.
- Exposes domain-specific methods that interact with the underlying MCP server.
- Communication typically via stdio or HTTP depending on the MCP server implementation.

## Communication Flow
1. Client instantiated.
2. `await client.initialize()` → loads config → creates server instances → runs health checks.
3. Method calls routed through server classes to the external MCP process.
4. Results returned synchronously or via async patterns.

## Extending with New Servers
1. Add entry to `mcp_config.json`.
2. Create `NewServer` class in `servers/new_server.py` inheriting `BaseMCPServer`.
3. Implement `health_check()`.
4. Register in `client.py` `_server_registry()`.
5. Expose via property if desired.
6. Update documentation and workflows.

## Key Benefits
- **Modularity**: Servers are independent and swappable.
- **Configurability**: No code changes needed to add tools.
- **Observability**: Built-in metrics and health checks.
- **Extensibility**: Clear pattern for new integrations.

This architecture enables efficient, maintainable multi-tool automation.
