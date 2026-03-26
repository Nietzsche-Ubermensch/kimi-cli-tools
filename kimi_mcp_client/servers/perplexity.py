"""Perplexity MCP server — research, Q&A, and reasoning via Perplexity API."""

from __future__ import annotations

import os
from typing import Any

from .base import BaseMCPServer

_MODELS = {
    "low": "sonar",
    "medium": "sonar-pro",
    "high": "sonar-reasoning",
    "quick": "sonar-pro",
    "comprehensive": "sonar-reasoning",
    "exhaustive": "sonar-deep-research",
}


class PerplexityServer(BaseMCPServer):
    """Perplexity AI for research and Q&A.

    Tools: ask, research, reason
    """

    _BASE_URL = "https://api.perplexity.ai"
    _TOOLS = ["ask", "research", "reason"]

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.api_key: str | None = (
            config.get("env", {}).get("PERPLEXITY_API_KEY")
            or os.environ.get("PERPLEXITY_API_KEY")
        )

    def _auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _require_key(self) -> None:
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY is not configured")

    async def health_check(self) -> dict[str, Any]:
        if not self.api_key:
            return {"status": "error", "error": "PERPLEXITY_API_KEY not set"}
        try:
            session = await self._get_session()
            async with session.post(
                f"{self._BASE_URL}/chat/completions",
                headers=self._auth_headers(),
                json={"model": "sonar", "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1},
            ) as resp:
                if resp.status == 200:
                    return {"status": "healthy", "api_key": f"{self.api_key[:8]}…", "tools": self._TOOLS}
                return {"status": "error", "error": f"HTTP {resp.status}"}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}

    async def _call_api(self, messages: list[dict[str, str]], model: str = "sonar-pro", max_tokens: int = 1000) -> dict[str, Any]:
        self._require_key()
        session = await self._get_session()
        async with session.post(
            f"{self._BASE_URL}/chat/completions",
            headers=self._auth_headers(),
            json={"model": model, "messages": messages, "max_tokens": max_tokens},
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            raise RuntimeError(f"Perplexity API error: HTTP {resp.status} — {await resp.text()}")

    async def ask(self, question: str, context_size: str = "medium") -> dict[str, Any]:
        """Quick factual Q&A with citations. context_size: low/medium/high."""
        self._track_request()
        model = _MODELS.get(context_size, "sonar-pro")
        result = await self._call_api([{"role": "user", "content": question}], model=model)
        message = result.get("choices", [{}])[0].get("message", {})
        return {
            "question": question,
            "answer": message.get("content", ""),
            "citations": result.get("citations", []),
            "model": model,
        }

    async def research(self, topic: str, depth: str = "comprehensive") -> dict[str, Any]:
        """Deep multi-source research. depth: quick/comprehensive/exhaustive."""
        self._track_request()
        model = _MODELS.get(depth, "sonar-reasoning")
        prompt = f"Conduct a thorough research on: {topic}. Provide a comprehensive analysis with key findings and sources."
        result = await self._call_api([{"role": "user", "content": prompt}], model=model, max_tokens=2000)
        message = result.get("choices", [{}])[0].get("message", {})
        return {
            "topic": topic,
            "depth": depth,
            "summary": message.get("content", ""),
            "sources": result.get("citations", []),
        }

    async def reason(self, problem: str, show_work: bool = True) -> dict[str, Any]:
        """Step-by-step logical reasoning."""
        self._track_request()
        suffix = " showing your work" if show_work else ""
        prompt = f"Solve this problem step by step{suffix}: {problem}"
        result = await self._call_api([{"role": "user", "content": prompt}], model="sonar-reasoning", max_tokens=2000)
        content: str = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        lines = [ln for ln in content.splitlines() if ln.strip()]
        conclusion = ""
        reasoning: list[str] = []
        for line in lines:
            if any(kw in line.lower() for kw in ("conclusion", "answer:", "therefore")):
                conclusion = line.split(":", 1)[-1].strip()
            else:
                reasoning.append(line)
        if not conclusion and reasoning:
            conclusion = reasoning.pop()

        return {
            "problem": problem,
            "reasoning": reasoning,
            "conclusion": conclusion,
        }
