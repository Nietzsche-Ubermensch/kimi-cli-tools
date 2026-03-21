"""
Execution Engine

Handles parallel and sequential tool execution with proper state management.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import logging

from .planner import ExecutionPlan, ToolCall

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result of a single tool execution."""
    tool_name: str
    inputs: Dict[str, Any]
    output: Any
    success: bool
    duration_ms: int
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ExecutionState:
    """State of an ongoing or completed execution."""
    plan_id: str
    status: str  # pending, running, completed, failed
    results: Dict[str, ToolResult] = field(default_factory=dict)
    current_step: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ExecutionContext:
    """Context passed between tool executions."""
    shared_memory: Dict[str, Any] = field(default_factory=dict)
    intermediate_results: List[ToolResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionEngine:
    """
    Executes tool workflows with parallel/sequential handling.
    """
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.active_executions: Dict[str, ExecutionState] = {}
        self.tool_registry: Dict[str, Callable] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def register_tool(self, name: str, handler: Callable) -> None:
        """Register a tool handler."""
        self.tool_registry[name] = handler
    
    async def execute(
        self,
        plan: ExecutionPlan,
        progress_callback: Optional[Callable[[str, Dict], None]] = None
    ) -> ExecutionState:
        """
        Execute a plan and return final state.
        
        Args:
            plan: Execution plan to run
            progress_callback: Optional callback for progress updates
            
        Returns:
            Final execution state
        """
        state = ExecutionState(
            plan_id=plan.plan_id,
            status="running",
            start_time=datetime.now().isoformat()
        )
        self.active_executions[plan.plan_id] = state
        
        context = ExecutionContext()
        context.metadata["plan"] = plan
        
        try:
            if plan.execution_mode == "parallel":
                await self._execute_parallel(
                    plan, state, context, progress_callback
                )
            elif plan.execution_mode == "sequential":
                await self._execute_sequential(
                    plan, state, context, progress_callback
                )
            else:  # mixed
                await self._execute_mixed(
                    plan, state, context, progress_callback
                )
            
            state.status = "completed"
            
        except Exception as e:
            state.status = "failed"
            state.error = str(e)
            logger.error(f"Execution failed: {e}")
            
        finally:
            state.end_time = datetime.now().isoformat()
        
        return state
    
    async def _execute_parallel(
        self,
        plan: ExecutionPlan,
        state: ExecutionState,
        context: ExecutionContext,
        progress_callback: Optional[Callable]
    ) -> None:
        """Execute all tools in parallel."""
        tasks = []
        
        for i, tool_call in enumerate(plan.tools):
            task = self._execute_tool_with_retry(
                tool_call, state, context, progress_callback
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Store results
        for i, result in enumerate(results):
            tool_name = plan.tools[i].name
            if isinstance(result, Exception):
                state.results[tool_name] = ToolResult(
                    tool_name=tool_name,
                    inputs=plan.tools[i].inputs,
                    output=None,
                    success=False,
                    duration_ms=0,
                    error=str(result)
                )
            else:
                state.results[tool_name] = result
    
    async def _execute_sequential(
        self,
        plan: ExecutionPlan,
        state: ExecutionState,
        context: ExecutionContext,
        progress_callback: Optional[Callable]
    ) -> None:
        """Execute tools one after another."""
        for i, tool_call in enumerate(plan.tools):
            state.current_step = i
            
            result = await self._execute_tool_with_retry(
                tool_call, state, context, progress_callback
            )
            
            state.results[tool_call.name] = result
            context.intermediate_results.append(result)
            
            # Update shared memory
            if result.success and result.output:
                context.shared_memory[f"{tool_call.name}_output"] = result.output
            
            if not result.success and not tool_call.parallel:
                # Stop on failure for sequential execution
                raise Exception(f"Tool {tool_call.name} failed: {result.error}")
    
    async def _execute_mixed(
        self,
        plan: ExecutionPlan,
        state: ExecutionState,
        context: ExecutionContext,
        progress_callback: Optional[Callable]
    ) -> None:
        """Execute with mixed parallel/sequential based on dependencies."""
        completed = set()
        remaining = list(range(len(plan.tools)))
        
        while remaining:
            # Find ready tasks (dependencies met)
            ready = []
            for idx in remaining:
                tool_call = plan.tools[idx]
                deps_met = all(
                    plan.tools[d].name in completed
                    for d in tool_call.depends_on
                )
                if deps_met:
                    ready.append(idx)
            
            if not ready:
                # Deadlock or missing dependencies
                raise Exception("Unable to resolve tool dependencies")
            
            # Execute ready tasks in parallel
            tasks = []
            for idx in ready:
                tasks.append(self._execute_tool_with_retry(
                    plan.tools[idx], state, context, progress_callback
                ))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for idx, result in zip(ready, results):
                tool_name = plan.tools[idx].name
                
                if isinstance(result, Exception):
                    state.results[tool_name] = ToolResult(
                        tool_name=tool_name,
                        inputs=plan.tools[idx].inputs,
                        output=None,
                        success=False,
                        duration_ms=0,
                        error=str(result)
                    )
                else:
                    state.results[tool_name] = result
                    context.intermediate_results.append(result)
                    if result.success and result.output:
                        context.shared_memory[f"{tool_name}_output"] = result.output
                
                completed.add(tool_name)
                remaining.remove(idx)
    
    async def _execute_tool_with_retry(
        self,
        tool_call: ToolCall,
        state: ExecutionState,
        context: ExecutionContext,
        progress_callback: Optional[Callable]
    ) -> ToolResult:
        """Execute a tool with retry logic."""
        start_time = datetime.now()
        last_error = None
        
        for attempt in range(tool_call.retry_count):
            try:
                # Update progress
                if progress_callback:
                    progress_callback("tool_start", {
                        "tool": tool_call.name,
                        "attempt": attempt + 1
                    })
                
                # Execute the tool
                handler = self.tool_registry.get(tool_call.name)
                if not handler:
                    raise ValueError(f"Unknown tool: {tool_call.name}")
                
                # Prepare inputs with context
                inputs = self._prepare_inputs(
                    tool_call.inputs,
                    context.shared_memory
                )
                
                # Execute (support both sync and async handlers)
                if asyncio.iscoroutinefunction(handler):
                    output = await handler(**inputs)
                else:
                    output = await asyncio.get_event_loop().run_in_executor(
                        self.executor,
                        lambda: handler(**inputs)
                    )
                
                duration = int(
                    (datetime.now() - start_time).total_seconds() * 1000
                )
                
                # Update progress
                if progress_callback:
                    progress_callback("tool_complete", {
                        "tool": tool_call.name,
                        "duration_ms": duration,
                        "success": True
                    })
                
                return ToolResult(
                    tool_name=tool_call.name,
                    inputs=inputs,
                    output=output,
                    success=True,
                    duration_ms=duration
                )
                
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Tool {tool_call.name} attempt {attempt + 1} failed: {e}"
                )
                
                if progress_callback:
                    progress_callback("tool_retry", {
                        "tool": tool_call.name,
                        "attempt": attempt + 1,
                        "error": last_error
                    })
                
                if attempt < tool_call.retry_count - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # All retries exhausted
        duration = int(
            (datetime.now() - start_time).total_seconds() * 1000
        )
        
        if progress_callback:
            progress_callback("tool_failed", {
                "tool": tool_call.name,
                "error": last_error
            })
        
        return ToolResult(
            tool_name=tool_call.name,
            inputs=tool_call.inputs,
            output=None,
            success=False,
            duration_ms=duration,
            error=last_error
        )
    
    def _prepare_inputs(
        self,
        inputs: Dict[str, Any],
        shared_memory: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare inputs with context substitution."""
        result = {}
        
        for key, value in inputs.items():
            if isinstance(value, str):
                # Substitute shared memory references
                if value.startswith("$memory."):
                    mem_key = value[8:]  # Remove $memory. prefix
                    value = shared_memory.get(mem_key, value)
                elif "{{" in value:
                    # Template substitution
                    for mem_key, mem_value in shared_memory.items():
                        placeholder = f"{{{{{mem_key}}}}}"
                        if placeholder in value:
                            value = value.replace(placeholder, str(mem_value))
            
            result[key] = value
        
        return result
    
    def get_execution_state(self, plan_id: str) -> Optional[ExecutionState]:
        """Get current state of an execution."""
        return self.active_executions.get(plan_id)
    
    def cancel_execution(self, plan_id: str) -> bool:
        """Cancel an ongoing execution."""
        if plan_id in self.active_executions:
            state = self.active_executions[plan_id]
            if state.status == "running":
                state.status = "cancelled"
                return True
        return False
