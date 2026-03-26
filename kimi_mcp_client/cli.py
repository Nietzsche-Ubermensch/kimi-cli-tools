#!/usr/bin/env python3
"""
Kimi MCP Client CLI
Command-line interface for MCP orchestration
"""

import asyncio
import argparse
import json
import sys
from typing import Dict, Any, List

from .client import KimiMCPClient, get_client


def _print_status(status: Dict[str, Any]) -> None:
    """Print a server-status dict produced by initialize() or health_check()."""
    print("\n" + "=" * 60)
    print("SERVER STATUS")
    print("=" * 60)
    for name, info in status.items():
        icon = "✅" if info.get("status") == "healthy" else "❌"
        print(f"{icon} {name:20s} {info.get('status', 'unknown')}")
        if "tools" in info:
            tools = info["tools"]
            if isinstance(tools, list):
                print(f"   Tools: {', '.join(tools[:5])}{'...' if len(tools) > 5 else ''}")
            else:
                print(f"   Tools: {tools}")
    healthy = sum(1 for s in status.values() if s.get("status") == "healthy")
    print(f"\nTotal: {healthy}/{len(status)} servers healthy")


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="kimi-mcp",
        description="Kimi MCP Client - 8-server orchestration"
    )
    
    parser.add_argument(
        "--yolo",
        action="store_true",
        help="Enable autonomous mode (no confirmation)"
    )
    
    parser.add_argument(
        "--config",
        default="mcp_config.json",
        help="MCP config file path"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check MCP server status")
    
    # Workflow commands
    workflow_parser = subparsers.add_parser("workflow", help="Run pre-built workflows")
    workflow_parser.add_argument("name", choices=[
        "research_to_linear",
        "bug_fix",
        "competitive_analysis",
        "scraper_build",
        "documentation_lookup"
    ], help="Workflow to run")
    workflow_parser.add_argument("--args", "-a", nargs="+", help="Workflow arguments")
    
    # Execute command
    exec_parser = subparsers.add_parser("exec", help="Execute direct command")
    exec_parser.add_argument("server", help="Server name")
    exec_parser.add_argument("tool", help="Tool to execute")
    exec_parser.add_argument("--params", "-p", help="JSON params")
    
    # Interactive mode
    subparsers.add_parser("interactive", help="Start interactive session")
    
    return parser


async def cmd_status(client: KimiMCPClient) -> int:
    """Execute status command."""
    print("🔍 Checking MCP server status...\n")
    status = await client.initialize()
    _print_status(status)
    return 0


async def cmd_workflow(client: KimiMCPClient, name: str, args: List[str]) -> int:
    """Execute workflow command."""
    print(f"🚀 Executing workflow: {name}\n")
    
    workflows = client.workflows
    
    if name == "research_to_linear":
        if len(args) < 2:
            print("Usage: workflow research_to_linear <topic> <team_id>")
            return 1
        result = await workflows.research_to_linear(args[0], args[1])
        print(f"\n✅ Created issue: {result['issue']['identifier']}")
        
    elif name == "bug_fix":
        if len(args) < 2:
            print("Usage: workflow bug_fix <issue_id> <repo>")
            return 1
        result = await workflows.bug_fix(args[0], args[1])
        print(f"\n✅ Created PR: {result['pr']['number']}")
        
    elif name == "competitive_analysis":
        if len(args) < 2:
            print("Usage: workflow competitive_analysis <query> <team_id>")
            return 1
        result = await workflows.competitive_analysis(args[0], args[1])
        print(f"\n✅ Created issue: {result['issue']['identifier']}")
        
    elif name == "scraper_build":
        if len(args) < 2:
            print("Usage: workflow scraper_build <url> <repo>")
            return 1
        result = await workflows.scraper_build(args[0], args[1])
        print(f"\n✅ Committed: {result['commit']['commit']['sha'][:8]}")
        
    elif name == "documentation_lookup":
        if len(args) < 2:
            print("Usage: workflow documentation_lookup <library> <question>")
            return 1
        result = await workflows.documentation_lookup(args[0], args[1])
        print(f"\n✅ Found documentation")
    
    else:
        print(f"Unknown workflow: {name}")
        return 1
    
    return 0


async def cmd_interactive(client: KimiMCPClient) -> int:
    """Start interactive session."""
    print("🎯 Kimi MCP Interactive Mode")
    print("Type 'help' for commands, 'exit' to quit\n")
    
    await client.initialize()
    
    while True:
        try:
            cmd = input("kimi-mcp> ").strip()
            
            if cmd in ("exit", "quit"):
                break
            
            if cmd == "help":
                print("\nCommands:")
                print("  status     - Check server status")
                print("  session    - Show session info")
                print("  workflows  - List available workflows")
                print("  exit       - Quit\n")
            
            elif cmd == "status":
                # Call health_check() directly — avoids re-initializing the
                # client (which would re-append to session.servers_used).
                status = {
                    name: await server.health_check()
                    for name, server in client._servers.items()
                }
                _print_status(status)
            
            elif cmd == "session":
                report = client.get_session_report()
                print(json.dumps(report, indent=2))
            
            elif cmd == "workflows":
                workflows = [
                    "research_to_linear <topic> <team_id>",
                    "bug_fix <issue_id> <repo>",
                    "competitive_analysis <query> <team_id>",
                    "scraper_build <url> <repo>",
                    "documentation_lookup <library> <question>"
                ]
                print("\nAvailable workflows:")
                for w in workflows:
                    print(f"  {w}")
                print()
            
            else:
                print(f"Unknown command: {cmd}")
        
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except EOFError:
            break
    
    print("\n👋 Goodbye!")
    return 0


async def main_async() -> int:
    """Main async entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize client
    client = KimiMCPClient(
        yolo_mode=args.yolo,
        config_path=args.config
    )
    
    try:
        if args.command == "status":
            return await cmd_status(client)
        
        elif args.command == "workflow":
            return await cmd_workflow(client, args.name, args.args or [])
        
        elif args.command == "interactive":
            return await cmd_interactive(client)
        
        else:
            print(f"Command not implemented: {args.command}")
            return 1
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def main() -> int:
    """Main entry point."""
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
