"""
Conductor MCP Server

A hybrid server combining Sequential Thinking + Everything + Memory
to provide automated multi-tool workflow orchestration.

Problem Solved: Manual tool selection and workflow chaining creates friction.
Users waste cognitive load deciding WHICH tool to use and HOW to chain them.

Hybrid Synergy:
- Sequential Thinking: Plans optimal tool execution sequences
- Everything: Wraps all 8 Kimi servers for unified access
- Memory: Learns from successful workflows, applies templates
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import asdict

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent

from .planner import WorkflowPlanner, ExecutionPlan
from .executor import ExecutionEngine, ExecutionState
from .synthesizer import ResultSynthesizer, SynthesisResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConductorServer:
    """
    MCP Server for Intent-Aware Orchestration.
    
    Combines planning, execution, and synthesis into a unified
    orchestration layer that eliminates manual tool selection.
    """
    
    def __init__(self):
        self.server = Server("conductor")
        self.planner = WorkflowPlanner()
        self.executor = ExecutionEngine()
        self.synthesizer = ResultSynthesizer()
        
        # Tool registry for Kimi MCP servers
        self.tool_adapters: Dict[str, Callable] = {}
        
        # Workflow history for learning
        self.workflow_history: List[Dict] = []
        
        # Register MCP handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP tool handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available Conductor tools."""
            return [
                Tool(
                    name="intent_to_execution",
                    description="""
                    Parse natural language intent into an optimized tool execution plan.
                    
                    This is the primary entry point - describe what you want to accomplish
                    and Conductor will determine which tools to use and how to chain them.
                    
                    Examples:
                    - "Research the best authentication libraries for Node.js"
                    - "Debug why my React app crashes on mobile"
                    - "Create a Linear issue for implementing OAuth"
                    - "Find documentation about Python asyncio patterns"
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "intent": {
                                "type": "string",
                                "description": "Natural language description of what you want to accomplish"
                            },
                            "context": {
                                "type": "object",
                                "description": "Additional context like tech stack, constraints, or preferences",
                                "properties": {
                                    "tech_stack": {"type": "array", "items": {"type": "string"}},
                                    "constraints": {"type": "array", "items": {"type": "string"}},
                                    "priority": {"type": "string", "enum": ["speed", "accuracy", "cost"]},
                                    "existing_knowledge": {"type": "string"}
                                }
                            }
                        },
                        "required": ["intent"]
                    }
                ),
                Tool(
                    name="auto_route",
                    description="""
                    Route a request to the most appropriate single tool.
                    
                    Use this when you want Conductor to select the best tool
                    for a specific task without full workflow orchestration.
                    
                    Examples:
                    - "Search for Python best practices" → routes to Perplexity
                    - "Find the npm package page" → routes to Brave
                    - "Get API docs for FastAPI" → routes to Context7
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "Specific task to route"
                            },
                            "required_output": {
                                "type": "string",
                                "enum": ["quick", "detailed", "structured"],
                                "description": "Desired output format"
                            }
                        },
                        "required": ["task"]
                    }
                ),
                Tool(
                    name="workflow_orchestrate",
                    description="""
                    Execute a multi-step workflow across multiple tools.
                    
                    Takes a structured workflow definition and orchestrates
                    execution with proper dependency management and error handling.
                    
                    Supports parallel, sequential, and mixed execution modes.
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "Optional identifier for this workflow"
                            },
                            "steps": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "tool": {"type": "string"},
                                        "inputs": {"type": "object"},
                                        "parallel": {"type": "boolean"},
                                        "depends_on": {"type": "array", "items": {"type": "integer"}},
                                        "timeout": {"type": "integer"}
                                    },
                                    "required": ["tool", "inputs"]
                                }
                            },
                            "synthesis_mode": {
                                "type": "string",
                                "enum": ["merge", "chain", "structured"]
                            }
                        },
                        "required": ["steps"]
                    }
                ),
                Tool(
                    name="context_preservation",
                    description="""
                    Maintain context across multiple tool interactions.
                    
                    Stores intermediate results and shared state so that
                    subsequent tool calls can build on previous results
                    without manual context passing.
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session to preserve context for"
                            },
                            "action": {
                                "type": "string",
                                "enum": ["store", "retrieve", "merge", "clear"]
                            },
                            "data": {
                                "type": "object",
                                "description": "Data to store (for store action)"
                            }
                        },
                        "required": ["session_id", "action"]
                    }
                ),
                Tool(
                    name="learn_workflow",
                    description="""
                    Save a successful workflow as a reusable template.
                    
                    Conductor learns from successful executions and can
                    apply these patterns to similar future intents.
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "plan_id": {
                                "type": "string",
                                "description": "ID of the plan to learn from"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags for categorizing this workflow"
                            },
                            "success_rating": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            }
                        },
                        "required": ["plan_id", "success_rating"]
                    }
                ),
                Tool(
                    name="get_execution_status",
                    description="Get status and results of an ongoing or completed execution.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "plan_id": {
                                "type": "string",
                                "description": "Execution plan ID"
                            }
                        },
                        "required": ["plan_id"]
                    }
                ),
                Tool(
                    name="explain_plan",
                    description="""
                    Explain the reasoning behind a plan's tool selection and sequencing.
                    
                    Provides transparency into why specific tools were chosen
                    and how they will be orchestrated.
                    """,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "intent": {"type": "string"},
                            "context": {"type": "object"}
                        },
                        "required": ["intent"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict) -> List[Any]:
            """Handle tool execution."""
            handlers = {
                "intent_to_execution": self._handle_intent_to_execution,
                "auto_route": self._handle_auto_route,
                "workflow_orchestrate": self._handle_workflow_orchestrate,
                "context_preservation": self._handle_context_preservation,
                "learn_workflow": self._handle_learn_workflow,
                "get_execution_status": self._handle_get_execution_status,
                "explain_plan": self._handle_explain_plan
            }
            
            handler = handlers.get(name)
            if not handler:
                raise ValueError(f"Unknown tool: {name}")
            
            return await handler(arguments)
    
    async def _handle_intent_to_execution(
        self,
        arguments: Dict
    ) -> List[TextContent]:
        """
        Handle intent_to_execution tool.
        
        Creates an execution plan from natural language intent,
        executes it, and returns synthesized results.
        """
        intent = arguments["intent"]
        context = arguments.get("context", {})
        
        logger.info(f"Processing intent: {intent[:50]}...")
        
        # Step 1: Create execution plan
        plan = self.planner.create_plan(intent, context)
        
        # Step 2: Execute plan
        def progress_callback(event: str, data: Dict):
            logger.info(f"Execution event: {event} - {data}")
        
        state = await self.executor.execute(plan, progress_callback)
        
        # Step 3: Synthesize results
        synthesis = self.synthesizer.synthesize(state, plan, intent)
        
        # Step 4: Record for learning
        self.workflow_history.append({
            "plan_id": plan.plan_id,
            "intent": intent,
            "intent_type": plan.intent_type,
            "tools_used": list(state.results.keys()),
            "success": state.status == "completed",
            "timestamp": datetime.now().isoformat()
        })
        
        # Return formatted result
        result = {
            "plan_id": plan.plan_id,
            "intent_type": plan.intent_type,
            "execution_mode": plan.execution_mode,
            "tools_used": list(state.results.keys()),
            "summary": synthesis.summary,
            "recommendations": synthesis.recommendations,
            "confidence": synthesis.confidence,
            "execution_summary": synthesis.execution_summary
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    async def _handle_auto_route(self, arguments: Dict) -> List[TextContent]:
        """
        Handle auto_route tool.
        
        Routes a task to the single most appropriate tool.
        """
        task = arguments["task"]
        output_format = arguments.get("required_output", "detailed")
        
        # Quick intent analysis for single tool selection
        analysis = self.planner.intent_analyzer.analyze(task)
        
        if analysis["suggested_tools"]:
            selected_tool = analysis["suggested_tools"][0]
            
            result = {
                "selected_tool": selected_tool,
                "reasoning": f"Selected based on intent type: {analysis['intent_type']}",
                "confidence": analysis["confidence"],
                "alternative_tools": analysis["suggested_tools"][1:3],
                "suggested_inputs": self.planner.intent_analyzer._generate_tool_inputs(
                    selected_tool, analysis, {"query": task}
                )
            }
        else:
            result = {
                "selected_tool": "perplexity",
                "reasoning": "Defaulting to general research tool",
                "confidence": 0.5
            }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _handle_workflow_orchestrate(
        self,
        arguments: Dict
    ) -> List[TextContent]:
        """
        Handle workflow_orchestrate tool.
        
        Executes a user-defined workflow with dependency management.
        """
        steps = arguments["steps"]
        synthesis_mode = arguments.get("synthesis_mode", "merge")
        
        # Convert to ExecutionPlan format
        from .planner import ToolCall
        
        tool_calls = [
            ToolCall(
                name=step["tool"],
                inputs=step["inputs"],
                parallel=step.get("parallel", True),
                depends_on=step.get("depends_on", []),
                timeout=step.get("timeout", 30)
            )
            for step in steps
        ]
        
        plan = ExecutionPlan(
            plan_id=arguments.get("workflow_id", "custom_workflow"),
            intent="custom workflow",
            intent_type="custom",
            tools=tool_calls,
            execution_mode="mixed",
            estimated_duration=len(steps) * 15,
            synthesis_strategy=synthesis_mode
        )
        
        # Execute
        state = await self.executor.execute(plan)
        
        # Synthesize
        synthesis = self.synthesizer.synthesize(
            state, plan, "custom workflow"
        )
        
        result = {
            "workflow_completed": state.status == "completed",
            "results_by_tool": {
                name: {
                    "success": r.success,
                    "duration_ms": r.duration_ms,
                    "has_output": r.output is not None
                }
                for name, r in state.results.items()
            },
            "synthesis": {
                "summary": synthesis.summary,
                "recommendations": synthesis.recommendations
            }
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _handle_context_preservation(
        self,
        arguments: Dict
    ) -> List[TextContent]:
        """
        Handle context_preservation tool.
        
        Manages shared state across tool interactions.
        """
        session_id = arguments["session_id"]
        action = arguments["action"]
        
        # Simple in-memory session storage (would be persistent in production)
        if not hasattr(self, '_sessions'):
            self._sessions = {}
        
        if action == "store":
            self._sessions[session_id] = arguments.get("data", {})
            result = {"status": "stored", "session_id": session_id}
        
        elif action == "retrieve":
            data = self._sessions.get(session_id, {})
            result = {"status": "retrieved", "data": data}
        
        elif action == "merge":
            existing = self._sessions.get(session_id, {})
            new_data = arguments.get("data", {})
            existing.update(new_data)
            self._sessions[session_id] = existing
            result = {"status": "merged", "session_id": session_id}
        
        elif action == "clear":
            if session_id in self._sessions:
                del self._sessions[session_id]
            result = {"status": "cleared", "session_id": session_id}
        
        else:
            result = {"status": "error", "message": f"Unknown action: {action}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _handle_learn_workflow(
        self,
        arguments: Dict
    ) -> List[TextContent]:
        """
        Handle learn_workflow tool.
        
        Saves a successful workflow as a reusable template.
        """
        plan_id = arguments["plan_id"]
        success_rating = arguments["success_rating"]
        tags = arguments.get("tags", [])
        
        # Find plan in history
        plan = None
        for entry in self.workflow_history:
            if entry.get("plan_id") == plan_id:
                # Create a minimal plan object for saving
                from .planner import ExecutionPlan, ToolCall
                plan = ExecutionPlan(
                    plan_id=plan_id,
                    intent=entry["intent"],
                    intent_type=entry["intent_type"],
                    tools=[],  # Would be populated from full history
                    execution_mode="parallel",
                    estimated_duration=0,
                    synthesis_strategy="merge"
                )
                break
        
        if plan:
            self.planner.save_template(plan, success_rating)
            result = {
                "status": "learned",
                "plan_id": plan_id,
                "success_rating": success_rating,
                "tags": tags
            }
        else:
            result = {
                "status": "error",
                "message": f"Plan {plan_id} not found in history"
            }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _handle_get_execution_status(
        self,
        arguments: Dict
    ) -> List[TextContent]:
        """Handle get_execution_status tool."""
        plan_id = arguments["plan_id"]
        
        state = self.executor.get_execution_state(plan_id)
        
        if state:
            result = {
                "plan_id": plan_id,
                "status": state.status,
                "current_step": state.current_step,
                "completed_tools": list(state.results.keys()),
                "error": state.error,
                "duration": self._calculate_duration(state)
            }
        else:
            result = {
                "status": "not_found",
                "message": f"No execution found for plan_id: {plan_id}"
            }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _handle_explain_plan(
        self,
        arguments: Dict
    ) -> List[TextContent]:
        """
        Handle explain_plan tool.
        
        Provides transparency into planning decisions.
        """
        intent = arguments["intent"]
        context = arguments.get("context", {})
        
        # Analyze without executing
        analysis = self.planner.intent_analyzer.analyze(intent, context)
        plan = self.planner.create_plan(intent, context)
        
        explanation = {
            "intent_analyzed": intent,
            "intent_type": analysis["intent_type"],
            "confidence": analysis["confidence"],
            "entities_detected": analysis["entities"],
            "execution_strategy": {
                "mode": plan.execution_mode,
                "estimated_duration_seconds": plan.estimated_duration,
                "synthesis_strategy": plan.synthesis_strategy
            },
            "tool_selection_reasoning": [
                {
                    "tool": call.name,
                    "purpose": self._explain_tool_purpose(call.name, analysis),
                    "parallel": call.parallel,
                    "depends_on": call.depends_on
                }
                for call in plan.tools
            ],
            "pattern_match": analysis.get("pattern_match")
        }
        
        return [TextContent(type="text", text=json.dumps(explanation, indent=2))]
    
    def _explain_tool_purpose(self, tool_name: str, analysis: Dict) -> str:
        """Generate human-readable explanation for tool selection."""
        explanations = {
            "perplexity": "Research and synthesize comprehensive information",
            "brave": "Discover relevant URLs and sources",
            "firecrawl": "Extract structured content from web pages",
            "github": "Search code patterns and examples",
            "linear": "Track tasks and project work",
            "chrome": "Debug and inspect web applications",
            "context7": "Retrieve accurate documentation and API references",
            "playwright": "Automate browser interactions and testing"
        }
        return explanations.get(tool_name, "Execute specialized operation")
    
    def _calculate_duration(self, state: ExecutionState) -> int:
        """Calculate execution duration in seconds."""
        if state.start_time and state.end_time:
            start = datetime.fromisoformat(state.start_time)
            end = datetime.fromisoformat(state.end_time)
            return int((end - start).total_seconds())
        return 0
    
    def register_tool_adapter(self, name: str, handler: Callable):
        """Register an adapter for a Kimi MCP server tool."""
        self.tool_adapters[name] = handler
        self.executor.register_tool(name, handler)
    
    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Entry point for the Conductor MCP server."""
    server = ConductorServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
