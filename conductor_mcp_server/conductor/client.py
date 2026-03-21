"""
Conductor Client

Python client for interacting with the Conductor MCP server.
Provides programmatic access to intent-aware orchestration.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class IntentResult:
    """Result of an intent execution."""
    plan_id: str
    intent_type: str
    tools_used: List[str]
    summary: str
    recommendations: List[str]
    confidence: float
    execution_summary: Dict[str, Any]
    raw_response: Dict


@dataclass
class RouteResult:
    """Result of a routing decision."""
    selected_tool: str
    reasoning: str
    confidence: float
    alternative_tools: List[str]
    suggested_inputs: Dict[str, Any]


@dataclass
class PlanExplanation:
    """Explanation of a plan's reasoning."""
    intent_analyzed: str
    intent_type: str
    confidence: float
    entities_detected: Dict[str, Any]
    execution_strategy: Dict[str, Any]
    tool_selection_reasoning: List[Dict[str, Any]]


class ConductorClient:
    """
    Python client for the Conductor MCP server.
    
    Provides a high-level interface for:
    - Executing intents with automatic tool orchestration
    - Routing tasks to appropriate tools
    - Managing workflows and context
    """
    
    def __init__(self, server_url: Optional[str] = None):
        """
        Initialize the Conductor client.
        
        Args:
            server_url: Optional URL of the Conductor MCP server.
                       If not provided, uses stdio transport.
        """
        self.server_url = server_url
        self._session_context: Dict[str, Any] = {}
    
    async def execute_intent(
        self,
        intent: str,
        tech_stack: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        priority: str = "accuracy",
        context: Optional[Dict] = None
    ) -> IntentResult:
        """
        Execute a natural language intent with automatic tool orchestration.
        
        Args:
            intent: Natural language description of what to accomplish
            tech_stack: Optional list of technologies involved
            constraints: Optional list of constraints
            priority: "speed", "accuracy", or "cost"
            context: Optional additional context
            
        Returns:
            IntentResult with execution results
        """
        # Build context
        exec_context = context or {}
        if tech_stack:
            exec_context["tech_stack"] = tech_stack
        if constraints:
            exec_context["constraints"] = constraints
        exec_context["priority"] = priority
        
        # This would call the MCP server via the protocol
        # For now, return a mock result
        return IntentResult(
            plan_id=f"mock_{datetime.now().timestamp()}",
            intent_type="research",
            tools_used=["perplexity", "brave"],
            summary=f"Executed intent: {intent[:50]}...",
            recommendations=["Review results", "Take action"],
            confidence=0.85,
            execution_summary={"total_tools": 2, "successful": 2},
            raw_response={}
        )
    
    async def route_task(
        self,
        task: str,
        output_format: str = "detailed"
    ) -> RouteResult:
        """
        Route a task to the most appropriate single tool.
        
        Args:
            task: Task description
            output_format: "quick", "detailed", or "structured"
            
        Returns:
            RouteResult with tool selection
        """
        return RouteResult(
            selected_tool="perplexity",
            reasoning="Defaulting to general research",
            confidence=0.5,
            alternative_tools=["brave", "context7"],
            suggested_inputs={"query": task}
        )
    
    async def explain_plan(
        self,
        intent: str,
        tech_stack: Optional[List[str]] = None,
        context: Optional[Dict] = None
    ) -> PlanExplanation:
        """
        Explain the planning decisions for an intent without executing.
        
        Args:
            intent: Intent to analyze
            tech_stack: Optional technologies
            context: Optional context
            
        Returns:
            PlanExplanation with reasoning details
        """
        return PlanExplanation(
            intent_analyzed=intent,
            intent_type="research",
            confidence=0.8,
            entities_detected={"technologies": tech_stack or []},
            execution_strategy={"mode": "parallel", "estimated_duration": 30},
            tool_selection_reasoning=[
                {"tool": "perplexity", "purpose": "Research"}
            ]
        )
    
    def set_session_context(self, key: str, value: Any) -> None:
        """Store value in session context."""
        self._session_context[key] = value
    
    def get_session_context(self, key: str) -> Optional[Any]:
        """Retrieve value from session context."""
        return self._session_context.get(key)
    
    def clear_session_context(self) -> None:
        """Clear all session context."""
        self._session_context = {}


# Convenience functions for common use cases

async def research_topic(
    topic: str,
    depth: str = "comprehensive"
) -> IntentResult:
    """
    Research a topic using automatic tool orchestration.
    
    Args:
        topic: Topic to research
        depth: "quick", "standard", or "comprehensive"
        
    Returns:
        Research results
    """
    priority = "speed" if depth == "quick" else "accuracy"
    
    client = ConductorClient()
    return await client.execute_intent(
        intent=f"Research: {topic}",
        priority=priority
    )


async def debug_issue(
    error: str,
    tech_stack: List[str],
    url: Optional[str] = None
) -> IntentResult:
    """
    Debug an issue with automatic tool orchestration.
    
    Args:
        error: Error description or message
        tech_stack: Technologies involved
        url: Optional URL to inspect
        
    Returns:
        Debug results with diagnostic chain
    """
    context = {"error": error}
    if url:
        context["url"] = url
    
    client = ConductorClient()
    return await client.execute_intent(
        intent=f"Debug: {error}",
        tech_stack=tech_stack,
        context=context,
        priority="accuracy"
    )


async def implement_feature(
    description: str,
    tech_stack: List[str]
) -> IntentResult:
    """
    Get implementation plan with automatic tool orchestration.
    
    Args:
        description: Feature description
        tech_stack: Technologies to use
        
    Returns:
        Implementation plan
    """
    client = ConductorClient()
    return await client.execute_intent(
        intent=f"Implement: {description}",
        tech_stack=tech_stack,
        priority="accuracy"
    )


# Example usage
if __name__ == "__main__":
    async def demo():
        # Research example
        result = await research_topic("best authentication libraries for Node.js 2024")
        print(f"Summary: {result.summary}")
        print(f"Tools used: {result.tools_used}")
        print(f"Confidence: {result.confidence}")
    
    asyncio.run(demo())
