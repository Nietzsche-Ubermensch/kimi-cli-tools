# MCP Server Architecture

## Overview
The Kimi MCP client uses a modular, config-driven architecture based on the Model Context Protocol (MCP). It allows seamless integration with multiple external tools (Linear, Slack, Notion, Perplexity, GitHub, etc.) through a unified Python interface.

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
... (rest of previous content remains)

## Key Benefits
... (updated with transport flexibility)