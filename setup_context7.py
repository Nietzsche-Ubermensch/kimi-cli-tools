#!/usr/bin/env python3
"""
Context7 MCP Server Setup Script
Automates the configuration of Context7 documentation lookup
"""

import os
import sys
import json
from pathlib import Path


def check_env_file():
    """Check if CONTEXT7_API_KEY exists in .env."""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    content = env_path.read_text()
    if "CONTEXT7_API_KEY" in content:
        print("✅ CONTEXT7_API_KEY found in .env")
        return True
    else:
        print("⚠️ CONTEXT7_API_KEY not found in .env")
        return False


def add_context7_to_env():
    """Add CONTEXT7_API_KEY placeholder to .env."""
    env_path = Path(".env")
    
    context7_config = """
# Context7 Documentation Lookup
# Get your API key from: https://upstash.com/
CONTEXT7_API_KEY=your-context7-api-key-here
"""
    
    with open(env_path, "a") as f:
        f.write(context7_config)
    
    print("✅ Added CONTEXT7_API_KEY placeholder to .env")


def verify_mcp_config():
    """Verify Context7 is in mcp_config.json."""
    config_path = Path("mcp_config.json")
    
    if not config_path.exists():
        print("❌ mcp_config.json not found")
        return False
    
    with open(config_path) as f:
        config = json.load(f)
    
    servers = config.get("mcpServers", {})
    
    if "context7" in servers:
        print("✅ Context7 server configured in mcp_config.json")
        return True
    else:
        print("⚠️ Context7 server NOT found in mcp_config.json")
        print("   Run: python setup_context7.py --fix-config")
        return False


def fix_mcp_config():
    """Add Context7 to mcp_config.json."""
    config_path = Path("mcp_config.json")
    
    with open(config_path) as f:
        config = json.load(f)
    
    if "context7" not in config.get("mcpServers", {}):
        config["mcpServers"]["context7"] = {
            "command": "npx",
            "args": ["-y", "@upstash/context7-mcp"]
        }
        
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        print("✅ Added Context7 server to mcp_config.json")
    else:
        print("ℹ️ Context7 server already configured")


def main():
    """Main setup routine."""
    print("=" * 60)
    print("Context7 MCP Server Setup")
    print("=" * 60)
    
    # Check arguments
    if "--fix-config" in sys.argv:
        fix_mcp_config()
        return
    
    if "--fix-env" in sys.argv:
        add_context7_to_env()
        return
    
    # Full setup check
    print("\n1. Checking .env file...")
    env_ok = check_env_file()
    
    print("\n2. Checking mcp_config.json...")
    config_ok = verify_mcp_config()
    
    print("\n" + "=" * 60)
    if env_ok and config_ok:
        print("✅ Context7 is fully configured!")
        print("\nTo get your API key:")
        print("  1. Visit https://upstash.com/")
        print("  2. Sign up / Log in")
        print("  3. Create a new Context7 instance")
        print("  4. Copy the API key to your .env file")
    else:
        print("⚠️ Context7 setup incomplete")
        print("\nTo fix:")
        if not env_ok:
            print("  python setup_context7.py --fix-env")
        if not config_ok:
            print("  python setup_context7.py --fix-config")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
