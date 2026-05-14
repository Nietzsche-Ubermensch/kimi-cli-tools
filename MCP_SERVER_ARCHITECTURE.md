# MCP Server Architecture

## Overview
The Kimi MCP client uses a modular, config-driven architecture based on the Model Context Protocol (MCP). It integrates the implemented server set (`firecrawl`, `perplexity`, `linear`, `github`, `brave`, `chrome`, `playwright`, `context7`) through a unified Python interface.

Servers are defined externally (via npx or Python) and orchestrated by the client.

## Transport Layer Protocols

MCP supports multiple transport mechanisms for client-server communication:

### 1. stdio (Standard Input/Output) - Default for Local Servers
- Used by most npx-based MCP servers (e.g., @modelcontextprotocol/server-linear).
- Communication via subprocess stdin/stdout.
- Pros: Simple, no network required, good for local tools.
- Current usage: Primary transport for Linear, GitHub, Perplexity, etc.
- Implementation note: Handled by the MCP SDK when spawning via `command` + `args` in config.

### 2. HTTP / Streamable HTTP
- Used for remote or web-based MCP servers.
- The BaseMCPServer uses `aiohttp` for HTTP sessions.
- Supports request/response and streaming.
- Config example in fetch server: uses `streamable_http` type with URL and headers.

### 3. Server-Sent Events (SSE)
- Common for real-time, event-driven MCP servers.
- Often combined with HTTP for bidirectional streaming.
- Useful for long-running operations or live updates.

### Current Implementation Status
- **BaseMCPServer**: Provides shared `aiohttp.ClientSession` for HTTP-based transports.
- **Config-driven spawning**: stdio servers are launched via subprocess based on mcp_config.json.
- **Gap**: No unified Transport abstraction layer yet. Each server type handles its protocol implicitly.

### Recommended Implementation for Transport Abstraction
To make the system more robust and extensible:

1. Create `transports/` package with:
   - `base_transport.py`: Abstract base with `send()`, `receive()`, `connect()`, `close()`.
   - `stdio_transport.py`: Subprocess-based stdio implementation.
   - `http_transport.py`: aiohttp-based HTTP/SSE implementation.
2. Update `BaseMCPServer` to accept a `transport` parameter.
3. Allow per-server transport selection in mcp_config.json.

Example future config:
```json
"linear": {
  "transport": "stdio",
  "command": "npx",
  ...
}
```

This would allow mixing local stdio servers with remote HTTP/SSE servers seamlessly.

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
- The repository config uses `${VAR}` placeholders, but the Python client does not resolve them. Resolve placeholders via external tooling or manual replacement before `client.initialize()`.
- Current key mapping differences:
  - Config key `brave-search` maps to in-process client server key `brave`.
  - Config key `chrome-devtools` maps to in-process client server key `chrome`.
  - Config key `fetch` is included to mirror the current `mcp_config.json`, but only keys defined in `KimiMCPClient._server_registry()` are initialized by the Python client.
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
- **Transport Flexibility**: Supports multiple communication protocols (stdio, HTTP, SSE) for diverse server types.

This architecture enables efficient, maintainable multi-tool automation with flexible transport options.
