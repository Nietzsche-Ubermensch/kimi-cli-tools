#!/usr/bin/env python3
"""
Context7 MCP Server Setup Script
Automates the configuration of Context7 documentation lookup.

Usage:
  python setup_context7.py              # Full setup check
  python setup_context7.py --fix-env    # Add CONTEXT7_API_KEY to .env
  python setup_context7.py --fix-config # Add context7 server to mcp_config.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ENV_PATH = Path(".env")
_CONFIG_PATH = Path("mcp_config.json")

# Context7 is powered by Upstash — no API key required for the public MCP server.
_CONTEXT7_ENV_BLOCK = (
    "\n# Context7 Documentation Lookup\n"
    "# Get your key from: https://upstash.com/\n"
    "CONTEXT7_API_KEY=your-context7-api-key-here\n"
)

_CONTEXT7_SERVER = {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"],
}


def check_env_file() -> bool:
    """Return True if CONTEXT7_API_KEY is already present in .env."""
    if not _ENV_PATH.exists():
        print("❌ .env file not found")
        return False
    if "CONTEXT7_API_KEY" in _ENV_PATH.read_text(encoding="utf-8"):
        print("✅ CONTEXT7_API_KEY found in .env")
        return True
    print("⚠️  CONTEXT7_API_KEY not found in .env")
    return False


def add_context7_to_env() -> None:
    """Append CONTEXT7_API_KEY placeholder to .env."""
    with _ENV_PATH.open("a", encoding="utf-8") as fh:
        fh.write(_CONTEXT7_ENV_BLOCK)
    print("✅ Added CONTEXT7_API_KEY placeholder to .env")


def verify_mcp_config() -> bool:
    """Return True if context7 server is already in mcp_config.json."""
    if not _CONFIG_PATH.exists():
        print("❌ mcp_config.json not found")
        return False
    with _CONFIG_PATH.open(encoding="utf-8") as fh:
        config = json.load(fh)
    if "context7" in config.get("mcpServers", {}):
        print("✅ Context7 server configured in mcp_config.json")
        return True
    print("⚠️  Context7 server NOT found in mcp_config.json")
    print("   Run: python setup_context7.py --fix-config")
    return False


def fix_mcp_config() -> None:
    """Add context7 entry to mcp_config.json if absent."""
    if not _CONFIG_PATH.exists():
        print("❌ mcp_config.json not found — cannot patch", file=sys.stderr)
        sys.exit(1)

    with _CONFIG_PATH.open(encoding="utf-8") as fh:
        config = json.load(fh)

    servers: dict = config.setdefault("mcpServers", {})
    if "context7" in servers:
        print("ℹ️  Context7 server already configured")
        return

    servers["context7"] = _CONTEXT7_SERVER
    with _CONFIG_PATH.open("w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
        fh.write("\n")
    print("✅ Added Context7 server to mcp_config.json")


def main() -> None:
    """Main setup routine."""
    print("=" * 60)
    print("Context7 MCP Server Setup")
    print("=" * 60)

    if "--fix-config" in sys.argv:
        fix_mcp_config()
        return

    if "--fix-env" in sys.argv:
        add_context7_to_env()
        return

    # Full setup check
    print("\n1. Checking .env file…")
    env_ok = check_env_file()

    print("\n2. Checking mcp_config.json…")
    config_ok = verify_mcp_config()

    print("\n" + "=" * 60)
    if env_ok and config_ok:
        print("✅ Context7 is fully configured!")
        print("\nTo obtain your API key:")
        print("  1. Visit https://upstash.com/")
        print("  2. Sign up / Log in")
        print("  3. Create a new Context7 instance")
        print("  4. Copy the API key into your .env file")
    else:
        print("⚠️  Context7 setup incomplete")
        print("\nTo fix:")
        if not env_ok:
            print("  python setup_context7.py --fix-env")
        if not config_ok:
            print("  python setup_context7.py --fix-config")
    print("=" * 60)


if __name__ == "__main__":
    main()
