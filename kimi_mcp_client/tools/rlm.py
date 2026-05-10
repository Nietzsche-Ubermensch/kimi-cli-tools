from __future__ import annotations

from .spec import ToolResult


async def rlm_exec(args: dict, llm_callback=None) -> ToolResult:
    if not args.get("allow_exec", False):
        return ToolResult(content="rlm_exec requires allow_exec=true", is_error=True)
    code = args.get("code", "")
    captured: list[str] = []

    async def llm_query(prompt: str) -> str:
        if llm_callback:
            return await llm_callback(prompt)
        return ""

    async def llm_query_batched(prompts: list[str]) -> list[str]:
        out = []
        for item in prompts:
            out.append(await llm_query(item))
        return out

    env = {
        "llm_query": llm_query,
        "llm_query_batched": llm_query_batched,
        "print": lambda *items: captured.append(" ".join(str(i) for i in items)),
    }
    exec(code, {"__builtins__": {}}, env)
    return ToolResult(content="\n".join(captured))
