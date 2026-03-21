#!/usr/bin/env python3
"""
Test MCP Servers via subprocess (actual npx calls)
"""

import subprocess
import json
import time
from datetime import datetime

# MCP Server configurations from mcp_config.json
SERVERS = {
    "perplexity": {
        "cmd": ["npx", "-y", "@modelcontextprotocol/server-perplexity"],
        "env": ["PERPLEXITY_API_KEY"],
        "test_tool": "ask"
    },
    "linear": {
        "cmd": ["npx", "-y", "@modelcontextprotocol/server-linear"],
        "env": ["LINEAR_API_KEY"],
        "test_tool": "linear_getViewer"
    },
    "github": {
        "cmd": ["npx", "-y", "@modelcontextprotocol/server-github"],
        "env": ["GITHUB_TOKEN"],
        "test_tool": "search_repositories"
    },
    "brave": {
        "cmd": ["npx", "-y", "@modelcontextprotocol/server-brave-search"],
        "env": ["BRAVE_API_KEY"],
        "test_tool": "brave_web_search"
    },
    "firecrawl": {
        "cmd": ["npx", "-y", "@mendableai/firecrawl-mcp-server"],
        "env": ["FIRECRAWL_API_KEY"],
        "test_tool": "firecrawl_map"
    },
    "chrome": {
        "cmd": ["npx", "-y", "@modelcontextprotocol/server-puppeteer"],
        "env": [],
        "test_tool": "list_pages"
    },
    "playwright": {
        "cmd": ["npx", "-y", "@executeautomation/playwright-mcp-server"],
        "env": [],
        "test_tool": "get_playwright_version"
    },
    "context7": {
        "cmd": ["npx", "-y", "@upstash/context7-mcp"],
        "env": ["CONTEXT7_API_KEY"],
        "test_tool": "resolve-library"
    }
}


def check_env_vars(server_name, server_config):
    """Check if required environment variables are set."""
    import os
    missing = []
    for env_var in server_config["env"]:
        if not os.getenv(env_var):
            missing.append(env_var)
    return missing


def test_server_simple(server_name, server_config):
    """Simple test - just check if npx can start the process."""
    print(f"\n{'='*60}")
    print(f"Testing: {server_name}")
    print(f"{'='*60}")
    
    # Check environment variables
    missing_env = check_env_vars(server_name, server_config)
    if missing_env:
        print(f"  ⚠️  Missing env vars: {', '.join(missing_env)}")
        return {"status": "skipped", "reason": f"Missing: {', '.join(missing_env)}"}
    
    # Try to start the process (just check if it runs briefly)
    try:
        print(f"  🚀 Starting: {' '.join(server_config['cmd'])}")
        
        # Start process with timeout
        proc = subprocess.Popen(
            server_config["cmd"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment to see if it starts
        time.sleep(2)
        
        # Check if still running
        if proc.poll() is None:
            # Process is still running - good sign
            proc.terminate()
            proc.wait(timeout=2)
            print(f"  ✅ Process started successfully")
            return {"status": "healthy", "note": "Process starts correctly"}
        else:
            # Process exited quickly
            stdout, stderr = proc.communicate()
            if "error" in stderr.lower() or "Error" in stderr:
                print(f"  ❌ Error: {stderr[:100]}")
                return {"status": "error", "error": stderr[:200]}
            else:
                print(f"  ⚠️  Process exited quickly (may need stdin input)")
                return {"status": "unknown", "note": "Exited quickly - may need MCP handshake"}
    
    except subprocess.TimeoutExpired:
        proc.kill()
        print(f"  ⚠️  Timeout - process may need interaction")
        return {"status": "timeout"}
    except FileNotFoundError as e:
        print(f"  ❌ Not found: {e}")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return {"status": "error", "error": str(e)}


def main():
    """Run all server tests."""
    print("\n" + "="*70)
    print("KIMI MCP CLIENT - SERVER STATUS CHECK")
    print("="*70)
    print(f"Time: {datetime.now().isoformat()}")
    print("Testing: All 8 configured MCP servers\n")
    
    results = {}
    
    for server_name, server_config in SERVERS.items():
        results[server_name] = test_server_simple(server_name, server_config)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    healthy = 0
    skipped = 0
    error = 0
    
    for server, result in results.items():
        status = result["status"]
        if status == "healthy":
            healthy += 1
            icon = "✅"
        elif status == "skipped":
            skipped += 1
            icon = "⏸️"
        else:
            error += 1
            icon = "❌"
        
        print(f"{icon} {server:20s} {status}")
    
    print(f"\n{'='*70}")
    print(f"Healthy: {healthy} | Skipped: {skipped} | Error: {error}")
    print(f"Total: {len(SERVERS)} servers")
    print("="*70)
    
    # Save report
    report = {
        "tested_at": datetime.now().isoformat(),
        "results": results,
        "summary": {
            "healthy": healthy,
            "skipped": skipped,
            "error": error,
            "total": len(SERVERS)
        }
    }
    
    with open("mcp_status_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved: mcp_status_report.json")
    
    return healthy == len(SERVERS) - skipped  # Success if all non-skipped are healthy


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
