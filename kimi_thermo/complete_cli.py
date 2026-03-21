#!/usr/bin/env python3
"""
Complete CLI - All Official Tools, Zero Friction
Professional audit dashboard with thermodynamic health scoring.
"""

import asyncio
import io
import sys
import json
from .dynamic_complete import DynamicCompleteClient

# Force UTF-8 stdout on Windows (box-drawing, emoji)
if sys.platform == "win32" and not isinstance(sys.stdout, io.TextIOWrapper):
    pass  # already wrapped
elif hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ANSI colors — pure Python, no dependencies
C = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "red":    "\033[91m",
    "cyan":   "\033[96m",
    "blue":   "\033[94m",
    "white":  "\033[97m",
    "mag":    "\033[95m",
}

BUDGET_CAP = 200.0


def _regime_display(regime: str) -> str:
    """Color-coded regime label with emoji."""
    if regime == "ACT":
        return f"{C['green']}🟢 ACT{C['reset']}"
    if regime == "HOLD":
        return f"{C['yellow']}🟡 HOLD{C['reset']}"
    return f"{C['red']}🔴 REFUSE{C['reset']}"


def _health_color(score: int) -> str:
    """Pick color based on health score."""
    if score >= 80:
        return C["green"]
    if score >= 60:
        return C["yellow"]
    return C["red"]


def print_formatted_audit(audit: dict) -> None:
    """Render a professional terminal dashboard from an audit dict."""

    # ── Header ──────────────────────────────────────────────────────
    print()
    print(f"{C['bold']}{C['cyan']}╔══════════════════════════════════════════════════════════════════════════╗{C['reset']}")
    print(f"{C['bold']}{C['cyan']}║                      KIMI THERMO · AUDIT REPORT                        ║{C['reset']}")
    print(f"{C['bold']}{C['cyan']}╚══════════════════════════════════════════════════════════════════════════╝{C['reset']}")
    print()

    # ── Budget status bar ───────────────────────────────────────────
    spent  = audit["total_spent_usd"]
    remain = audit["budget_remaining"]
    pct    = (spent / BUDGET_CAP) * 100 if spent > 0 else 0
    filled = min(20, int(pct // 5))
    bar    = "█" * filled + "░" * (20 - filled)

    if remain > 100:
        status = "🟢 HEALTHY"
        bar_color = C["green"]
    elif remain > 50:
        status = "🟡 WARNING"
        bar_color = C["yellow"]
    else:
        status = "🔴 CRITICAL"
        bar_color = C["red"]

    print(f"  {C['bold']}Budget Status:{C['reset']}  {status}")
    print(f"    Spent:     {C['bold']}${spent:>8.2f}{C['reset']} / ${BUDGET_CAP:.2f}   "
          f"{bar_color}[{bar}]{C['reset']} {pct:.1f}%")
    print(f"    Remaining: {C['bold']}${remain:>8.2f}{C['reset']}")
    print()

    # ── Health score ────────────────────────────────────────────────
    thermo = audit.get("thermodynamic_states", {})
    t_stars = [s["T_star"] for s in thermo.values()]
    avg_t   = sum(t_stars) / len(t_stars) if t_stars else 0.0
    # Scale average T* (typically −2..+2) into 0-100
    health  = max(0, min(100, int(50 + avg_t * 25)))
    hc      = _health_color(health)

    print(f"  {C['bold']}Overall Health:{C['reset']}  "
          f"{hc}{C['bold']}{health}{C['reset']}/100  "
          f"{C['dim']}(avg T* = {avg_t:+.3f}){C['reset']}")
    print()

    # ── Tool usage table ────────────────────────────────────────────
    breakdown = audit.get("tool_breakdown", {})

    # Sort by total spend descending
    sorted_tools = sorted(
        breakdown.items(),
        key=lambda kv: kv[1]["total_spent"],
        reverse=True,
    )

    col_w = (18, 7, 10, 9, 14, 12)  # name, calls, spent, T*, regime, avg
    header = (
        f"{'Tool':<{col_w[0]}}"
        f"{'Calls':>{col_w[1]}}"
        f"{'Spent':>{col_w[2]}}"
        f"{'T*':>{col_w[3]}}"
        f"  {'Regime':<{col_w[4]}}"
        f"{'Avg $/call':>{col_w[5]}}"
    )
    rule = "─" * 76

    print(f"  {C['bold']}Tool Usage Breakdown{C['reset']}  {C['dim']}(sorted by spend){C['reset']}")
    print(f"  {rule}")
    print(f"  {C['bold']}{header}{C['reset']}")
    print(f"  {rule}")

    total_calls = 0
    for name, data in sorted_tools:
        state   = thermo.get(name, {})
        t_val   = state.get("T_star", 0.0)
        regime  = state.get("regime", "?")
        calls   = data.get("calls", 0)
        t_spent = data.get("total_spent", 0.0)
        avg_c   = data.get("avg_cost", 0.0)
        total_calls += calls

        # Color the T* value
        if t_val > 0.5:
            tc = C["green"]
        elif t_val > -0.5:
            tc = C["yellow"]
        else:
            tc = C["red"]

        print(
            f"  {name:<{col_w[0]}}"
            f"{calls:>{col_w[1]},}"
            f"{'${:.4f}'.format(t_spent):>{col_w[2]}}"
            f"  {tc}{t_val:>+7.3f}{C['reset']}"
            f"  {_regime_display(regime):<{col_w[4] + 9}}"  # +9 for ANSI codes
            f"{'${:.4f}'.format(avg_c):>{col_w[5]}}"
        )

    print(f"  {rule}")

    est_searches = int(remain / 0.02) if remain > 0 else 0
    est_utility  = int(remain / 0.001) if remain > 0 else 0
    print(f"  {C['bold']}Totals:{C['reset']}  {total_calls:,} calls   │   "
          f"Est. remaining: ~{est_searches:,} web searches  ·  ~{est_utility:,} utility calls")
    print()

    # ── Quick insights ──────────────────────────────────────────────
    print(f"  {C['bold']}{C['cyan']}Quick Insights{C['reset']}")
    print(f"  {'─' * 40}")

    if total_calls == 0:
        print(f"  {C['dim']}—{C['reset']} No calls yet — health score will update after first query.")
    elif health >= 80:
        print(f"  {C['green']}✓{C['reset']} All tools operating in optimal thermodynamic regime.")
    elif health >= 60:
        print(f"  {C['yellow']}▲{C['reset']} Monitor high-γ tools (web_search, memory) — approaching regime boundary.")
    else:
        print(f"  {C['red']}✗{C['reset']} Some tools approaching collapse — consider lighter queries or fast mode.")

    # Flag tools in HOLD/REFUSE only if they've actually been called
    problem_tools = [
        n for n, s in thermo.items()
        if s.get("regime") in ("HOLD", "REFUSE")
        and breakdown.get(n, {}).get("calls", 0) > 0
    ]
    if problem_tools:
        print(f"  {C['yellow']}▲{C['reset']} Non-ACT tools: {', '.join(problem_tools)}")

    if spent > 150:
        print(f"  {C['red']}⚠{C['reset']}  Budget critically low — switch to fast mode or reduce web calls.")
    elif spent > 100:
        print(f"  {C['yellow']}⚠{C['reset']}  Budget past 50% — review tool spend distribution.")

    if total_calls == 0:
        print(f"  {C['dim']}ℹ  No tool calls recorded yet. Run a query to populate audit data.{C['reset']}")

    print()


async def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Complete Kimi CLI — All Official Tools")
        print()
        print("Usage:")
        print('  python -m kimi_thermo.complete_cli "your query"')
        print("  python -m kimi_thermo.complete_cli --audit")
        print("  python -m kimi_thermo.complete_cli --audit-json")
        print("  python -m kimi_thermo.complete_cli --tools")
        print("  python -m kimi_thermo.complete_cli --costs")
        print()
        print("Examples:")
        print('  Search:    "latest AI news"')
        print('  Code:      "write a python function to sort dicts"')
        print('  Convert:   "convert 100 USD to EUR"')
        print('  Excel:     "analyze this data.xlsx file"')
        print('  Cat:       "give me a cat blessing 🐱"')
        return

    client = DynamicCompleteClient()

    # ── --audit: formatted dashboard ────────────────────────────────
    if args[0] == "--audit":
        audit = client.get_full_audit()
        print_formatted_audit(audit)
        await client.close()
        return

    # ── --audit-json: raw JSON for piping / scripts ─────────────────
    if args[0] == "--audit-json":
        audit = client.get_full_audit()
        print(json.dumps(audit, indent=2))
        await client.close()
        return

    # ── --tools: list all 13 formula tools ──────────────────────────
    if args[0] == "--tools":
        from .tools_complete import OFFICIAL_TOOLS
        print("All 13 Official Tools:")
        for name, meta in OFFICIAL_TOOLS.items():
            protected = "🔒" if meta.protected else "  "
            cost = {
                "web_search": "~$0.02", "fetch": "~$0.01",
                "code_runner": "~$0.01", "quickjs": "~$0.01",
                "excel": "~$0.01", "memory": "~$0.005",
            }.get(name, "~$0.001")
            print(f"  {protected} {name:20} γ={meta.base_gamma:.2f}  "
                  f"{cost:8}  {meta.description[:40]}...")
        await client.close()
        return

    # ── --costs: estimated pricing table ────────────────────────────
    if args[0] == "--costs":
        print("Estimated Costs (USD):")
        print("  web_search:    $0.02 per search")
        print("  fetch:         $0.01 per fetch")
        print("  code_runner:   $0.01 per execution")
        print("  excel:         $0.01 per file")
        print("  memory:        $0.005 per operation")
        print("  All others:    ~$0.001 per call")
        print()
        print("With $200 budget: ~10,000 web searches or ~200,000 utility calls")
        await client.close()
        return

    # ── Query execution ─────────────────────────────────────────────
    query = " ".join(args)
    print(f"[Processing: {query[:60]}...]", file=sys.stderr)

    result = await client.execute(query)

    print(result["output"])

    if result.get("tools_used"):
        print(f"\n[Tools: {', '.join(result['tools_used'])}]", file=sys.stderr)
    print(
        f"[Cost: ${result['cost']:.4f} | "
        f"Total: ${result['total_spent']:.2f} | "
        f"Remaining: ${result['budget_remaining']:.2f}]",
        file=sys.stderr,
    )

    await client.close()


def _cli_entry():
    asyncio.run(main())

if __name__ == "__main__":
    _cli_entry()
