"""
Workflow Planner

Analyzes intent and generates optimized tool execution plans.
Combines Sequential Thinking (planning) + Memory (templates).
"""

import re
import json
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import hashlib


@dataclass
class ToolCall:
    """A single tool call in a workflow."""
    name: str
    inputs: Dict[str, Any]
    parallel: bool = True
    depends_on: List[int] = field(default_factory=list)
    timeout: int = 30
    retry_count: int = 2


@dataclass
class ExecutionPlan:
    """Complete execution plan for an intent."""
    plan_id: str
    intent: str
    intent_type: str
    tools: List[ToolCall]
    execution_mode: str  # parallel, sequential, mixed
    estimated_duration: int  # seconds
    synthesis_strategy: str  # merge, prioritize, custom
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class IntentPattern:
    """Learned pattern for intent classification."""
    pattern_id: str
    regex_pattern: str
    tool_sequence: List[str]
    success_rate: float
    avg_execution_time: float
    example_intents: List[str]


class IntentAnalyzer:
    """Analyzes user intent to determine required tools and approach."""
    
    # Intent classification patterns
    INTENT_PATTERNS = {
        "research": {
            "keywords": ["research", "find", "best", "compare", "what is", "how to", "learn"],
            "default_tools": ["perplexity", "brave", "context7"],
            "parallel": True
        },
        "debug": {
            "keywords": ["debug", "error", "fix", "broken", "not working", "issue", "problem"],
            "default_tools": ["chrome", "github", "perplexity"],
            "parallel": False
        },
        "implement": {
            "keywords": ["implement", "add", "create", "build", "code", "develop"],
            "default_tools": ["perplexity", "context7", "github", "linear"],
            "parallel": False
        },
        "investigate": {
            "keywords": ["investigate", "analyze", "check", "look at", "review"],
            "default_tools": ["brave", "firecrawl", "chrome"],
            "parallel": True
        },
        "document": {
            "keywords": ["document", "write", "explain", "summarize", "describe"],
            "default_tools": ["perplexity", "github"],
            "parallel": False
        }
    }
    
    # Tool capability mappings
    TOOL_CAPABILITIES = {
        "perplexity": {
            "capabilities": ["research", "qa", "analysis", "synthesis"],
            "inputs": ["query", "context", "search_context_size"],
            "output_type": "text/analysis",
            "speed": "medium",
            "cost": "medium"
        },
        "brave": {
            "capabilities": ["search", "discovery", "url_finding"],
            "inputs": ["query", "count"],
            "output_type": "urls/snippets",
            "speed": "fast",
            "cost": "low"
        },
        "firecrawl": {
            "capabilities": ["scrape", "extract", "crawl"],
            "inputs": ["url", "formats"],
            "output_type": "structured_content",
            "speed": "medium",
            "cost": "medium"
        },
        "github": {
            "capabilities": ["code_search", "pr_create", "issue_track"],
            "inputs": ["query", "repo", "owner"],
            "output_type": "code/issues",
            "speed": "fast",
            "cost": "low"
        },
        "linear": {
            "capabilities": ["issue_create", "project_track", "task_manage"],
            "inputs": ["title", "description", "team_id"],
            "output_type": "issues/projects",
            "speed": "fast",
            "cost": "low"
        },
        "chrome": {
            "capabilities": ["debug", "inspect", "test_ui"],
            "inputs": ["url", "selector"],
            "output_type": "dom/console",
            "speed": "fast",
            "cost": "low"
        },
        "context7": {
            "capabilities": ["docs_lookup", "api_reference", "examples"],
            "inputs": ["library", "question"],
            "output_type": "documentation",
            "speed": "fast",
            "cost": "low"
        },
        "playwright": {
            "capabilities": ["test", "automate", "e2e"],
            "inputs": ["script", "url"],
            "output_type": "test_results",
            "speed": "slow",
            "cost": "medium"
        }
    }
    
    def __init__(self):
        self.learned_patterns: List[IntentPattern] = []
        self._load_learned_patterns()
    
    def _load_learned_patterns(self):
        """Load previously learned intent patterns."""
        patterns_file = Path("conductor_patterns.json")
        if patterns_file.exists():
            with open(patterns_file, 'r') as f:
                data = json.load(f)
                self.learned_patterns = [
                    IntentPattern(**p) for p in data.get("patterns", [])
                ]
    
    def analyze(self, intent: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze user intent to determine type, required tools, and approach.
        
        Args:
            intent: User's natural language intent
            context: Additional context (tech stack, constraints, etc.)
            
        Returns:
            Analysis result with intent type, confidence, suggested tools
        """
        intent_lower = intent.lower()
        context = context or {}
        
        # Step 1: Classify intent type
        intent_type, confidence = self._classify_intent_type(intent_lower)
        
        # Step 2: Extract entities
        entities = self._extract_entities(intent_lower, context)
        
        # Step 3: Determine required tools
        tools = self._select_tools(intent_type, entities, context)
        
        # Step 4: Check for learned patterns
        pattern_match = self._match_learned_pattern(intent_lower)
        if pattern_match and pattern_match.success_rate > 0.8:
            # Use learned tool sequence if high confidence
            tools = self._merge_tool_sequences(tools, pattern_match.tool_sequence)
        
        # Step 5: Determine execution mode
        execution_mode = self._determine_execution_mode(intent_type, tools)
        
        return {
            "intent_type": intent_type,
            "confidence": confidence,
            "entities": entities,
            "suggested_tools": tools,
            "execution_mode": execution_mode,
            "pattern_match": pattern_match.pattern_id if pattern_match else None
        }
    
    def _classify_intent_type(self, intent: str) -> Tuple[str, float]:
        """Classify the intent into a type with confidence."""
        scores = {}
        
        for intent_type, config in self.INTENT_PATTERNS.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword in intent:
                    score += 1
            scores[intent_type] = score
        
        # Get highest scoring type
        if max(scores.values()) > 0:
            best_type = max(scores, key=scores.get)
            confidence = min(scores[best_type] / 2, 1.0)  # Normalize
            return best_type, confidence
        
        return "general", 0.5
    
    def _extract_entities(self, intent: str, context: Dict) -> Dict[str, Any]:
        """Extract key entities from intent and context."""
        entities = {
            "technologies": [],
            "actions": [],
            "outputs": [],
            "constraints": []
        }
        
        # Extract technologies (common tech stack items)
        tech_patterns = [
            r'\b(react|vue|angular|node\.?js|python|go|rust|java|kotlin|swift)\b',
            r'\b(postgres|mysql|mongodb|redis|elasticsearch)\b',
            r'\b(aws|gcp|azure|docker|kubernetes)\b',
            r'\b(graphql|rest|grpc|websocket)\b',
            r'\b(jwt|oauth|sso|auth)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, intent, re.IGNORECASE)
            entities["technologies"].extend(matches)
        
        # Extract from context
        if "tech_stack" in context:
            entities["technologies"].extend(context["tech_stack"])
        
        if "constraints" in context:
            entities["constraints"].extend(context["constraints"])
        
        # Deduplicate
        entities["technologies"] = list(set(entities["technologies"]))
        
        return entities
    
    def _select_tools(
        self,
        intent_type: str,
        entities: Dict,
        context: Dict
    ) -> List[str]:
        """Select appropriate tools based on intent and entities."""
        base_tools = self.INTENT_PATTERNS.get(intent_type, {}).get(
            "default_tools", ["perplexity", "brave"]
        ).copy()
        
        # Add context-specific tools
        if entities.get("technologies"):
            # Likely needs documentation
            if "context7" not in base_tools:
                base_tools.append("context7")
        
        if "implement" in intent_type or "code" in str(context).lower():
            if "github" not in base_tools:
                base_tools.append("github")
            if "linear" not in base_tools:
                base_tools.append("linear")
        
        if "error" in str(context).lower() or "debug" in intent_type:
            if "chrome" not in base_tools:
                base_tools.insert(0, "chrome")
        
        return base_tools
    
    def _match_learned_pattern(self, intent: str) -> Optional[IntentPattern]:
        """Match intent against learned patterns."""
        for pattern in self.learned_patterns:
            if re.search(pattern.regex_pattern, intent, re.IGNORECASE):
                return pattern
        return None
    
    def _merge_tool_sequences(
        self,
        base_tools: List[str],
        learned_tools: List[str]
    ) -> List[str]:
        """Merge base tool selection with learned sequence."""
        # Start with learned sequence
        merged = learned_tools.copy()
        
        # Add any missing base tools
        for tool in base_tools:
            if tool not in merged:
                merged.append(tool)
        
        return merged
    
    def _determine_execution_mode(
        self,
        intent_type: str,
        tools: List[str]
    ) -> str:
        """Determine optimal execution mode."""
        # Check if intent type prefers parallel
        pattern_config = self.INTENT_PATTERNS.get(intent_type, {})
        
        if pattern_config.get("parallel", False) and len(tools) > 1:
            return "parallel"
        elif len(tools) == 1:
            return "sequential"
        else:
            return "mixed"


class WorkflowPlanner:
    """
    Plans optimal tool execution workflows.
    
    Combines Sequential Thinking (dependency resolution) 
    with Memory (template retrieval).
    """
    
    def __init__(self):
        self.intent_analyzer = IntentAnalyzer()
        self.workflow_templates: Dict[str, Dict] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load workflow templates."""
        templates_file = Path("conductor_templates.json")
        if templates_file.exists():
            with open(templates_file, 'r') as f:
                self.workflow_templates = json.load(f)
    
    def create_plan(
        self,
        intent: str,
        context: Optional[Dict] = None
    ) -> ExecutionPlan:
        """
        Create execution plan for an intent.
        
        Args:
            intent: User intent
            context: Additional context
            
        Returns:
            Complete execution plan
        """
        # Analyze intent
        analysis = self.intent_analyzer.analyze(intent, context)
        
        # Generate plan ID
        plan_id = self._generate_plan_id(intent, context)
        
        # Check for exact template match
        template = self._find_matching_template(intent, analysis)
        
        if template:
            # Use template as base
            tool_calls = self._instantiate_template(template, context)
        else:
            # Generate plan from scratch
            tool_calls = self._generate_tool_calls(analysis, context)
        
        # Build dependency DAG
        tool_calls = self._build_dependencies(tool_calls)
        
        # Estimate duration
        estimated_duration = self._estimate_duration(tool_calls)
        
        # Determine synthesis strategy
        synthesis_strategy = self._select_synthesis_strategy(analysis)
        
        return ExecutionPlan(
            plan_id=plan_id,
            intent=intent,
            intent_type=analysis["intent_type"],
            tools=tool_calls,
            execution_mode=analysis["execution_mode"],
            estimated_duration=estimated_duration,
            synthesis_strategy=synthesis_strategy
        )
    
    def _generate_plan_id(self, intent: str, context: Optional[Dict]) -> str:
        """Generate unique plan ID."""
        hash_input = f"{intent}:{json.dumps(context, sort_keys=True)}:{datetime.now().isoformat()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def _find_matching_template(
        self,
        intent: str,
        analysis: Dict
    ) -> Optional[Dict]:
        """Find matching workflow template."""
        intent_type = analysis["intent_type"]
        
        # Look for templates matching intent type
        for template_id, template in self.workflow_templates.items():
            if template.get("intent_type") == intent_type:
                # Check if entities match
                required_entities = template.get("required_entities", [])
                found_entities = analysis["entities"]
                
                # Simple matching - can be enhanced
                if all(
                    any(req in found_entities.get("technologies", [])
                        for req in required_entities)
                    or not required_entities
                ):
                    return template
        
        return None
    
    def _instantiate_template(
        self,
        template: Dict,
        context: Optional[Dict]
    ) -> List[ToolCall]:
        """Instantiate a template with context variables."""
        tool_calls = []
        
        for step in template.get("steps", []):
            # Substitute variables in inputs
            inputs = self._substitute_variables(step.get("inputs", {}), context)
            
            tool_calls.append(ToolCall(
                name=step["tool"],
                inputs=inputs,
                parallel=step.get("parallel", True),
                depends_on=step.get("depends_on", []),
                timeout=step.get("timeout", 30),
                retry_count=step.get("retry_count", 2)
            ))
        
        return tool_calls
    
    def _substitute_variables(
        self,
        inputs: Dict,
        context: Optional[Dict]
    ) -> Dict:
        """Substitute template variables with context values."""
        if not context:
            return inputs
        
        result = {}
        for key, value in inputs.items():
            if isinstance(value, str) and "{{" in value:
                # Simple template substitution
                for ctx_key, ctx_value in context.items():
                    placeholder = f"{{{{{ctx_key}}}}}"
                    if placeholder in value:
                        value = value.replace(placeholder, str(ctx_value))
            result[key] = value
        
        return result
    
    def _generate_tool_calls(
        self,
        analysis: Dict,
        context: Optional[Dict]
    ) -> List[ToolCall]:
        """Generate tool calls from analysis."""
        tool_calls = []
        suggested_tools = analysis["suggested_tools"]
        
        # Generate inputs for each tool based on intent and context
        for i, tool_name in enumerate(suggested_tools):
            inputs = self._generate_tool_inputs(
                tool_name,
                analysis,
                context
            )
            
            tool_calls.append(ToolCall(
                name=tool_name,
                inputs=inputs,
                parallel=analysis["execution_mode"] == "parallel",
                depends_on=[],  # Will be populated by _build_dependencies
                timeout=30,
                retry_count=2
            ))
        
        return tool_calls
    
    def _generate_tool_inputs(
        self,
        tool_name: str,
        analysis: Dict,
        context: Optional[Dict]
    ) -> Dict:
        """Generate appropriate inputs for a tool."""
        intent = analysis.get("intent_type", "general")
        entities = analysis.get("entities", {})
        
        inputs = {}
        
        if tool_name == "perplexity":
            inputs["messages"] = [
                {
                    "role": "user",
                    "content": context.get("query", "Research requested topic")
                }
            ]
            inputs["search_context_size"] = "high"
        
        elif tool_name == "brave":
            query = context.get("query", "")
            if entities.get("technologies"):
                query += " " + " ".join(entities["technologies"])
            inputs["query"] = query
            inputs["count"] = 10
        
        elif tool_name == "context7":
            if entities.get("technologies"):
                inputs["library"] = entities["technologies"][0]
            inputs["question"] = context.get("query", "How to implement?")
        
        elif tool_name == "github":
            if "error" in str(context).lower():
                inputs["q"] = f"{context.get('error', '')} in:file"
            else:
                inputs["q"] = context.get("query", "")
        
        elif tool_name == "linear":
            inputs["title"] = context.get("title", "Task from Conductor")
            inputs["description"] = context.get("description", "")
            inputs["teamId"] = context.get("team_id", "")
        
        elif tool_name == "chrome":
            inputs["type"] = "url"
            inputs["url"] = context.get("url", "")
        
        return inputs
    
    def _build_dependencies(self, tool_calls: List[ToolCall]) -> List[ToolCall]:
        """Build dependency graph between tool calls."""
        # For now, simple sequential dependencies if not parallel
        # Can be enhanced with data flow analysis
        
        result = []
        for i, call in enumerate(tool_calls):
            new_call = ToolCall(
                name=call.name,
                inputs=call.inputs,
                parallel=call.parallel,
                depends_on=[i-1] if i > 0 and not call.parallel else [],
                timeout=call.timeout,
                retry_count=call.retry_count
            )
            result.append(new_call)
        
        return result
    
    def _estimate_duration(self, tool_calls: List[ToolCall]) -> int:
        """Estimate total execution duration."""
        total = 0
        parallel_group = 0
        
        for call in tool_calls:
            tool_speed = self.intent_analyzer.TOOL_CAPABILITIES.get(
                call.name, {}
            ).get("speed", "medium")
            
            duration = {
                "fast": 5,
                "medium": 15,
                "slow": 45
            }.get(tool_speed, 15)
            
            if call.parallel:
                parallel_group = max(parallel_group, duration)
            else:
                total += parallel_group + duration
                parallel_group = 0
        
        total += parallel_group
        return total
    
    def _select_synthesis_strategy(self, analysis: Dict) -> str:
        """Select result synthesis strategy."""
        intent_type = analysis["intent_type"]
        
        strategies = {
            "research": "merge_and_prioritize",
            "debug": "diagnostic_chain",
            "implement": "structured_plan",
            "investigate": "evidence_summary",
            "document": "narrative_merge"
        }
        
        return strategies.get(intent_type, "simple_merge")
    
    def save_template(
        self,
        plan: ExecutionPlan,
        success_rating: float
    ) -> None:
        """Save successful plan as template for future use."""
        if success_rating < 0.7:
            return  # Only save high-quality workflows
        
        template_id = f"template_{plan.intent_type}_{datetime.now().strftime('%Y%m%d')}"
        
        template = {
            "template_id": template_id,
            "intent_type": plan.intent_type,
            "required_entities": [],  # Extract from plan
            "steps": [
                {
                    "tool": call.name,
                    "inputs": call.inputs,
                    "parallel": call.parallel,
                    "depends_on": call.depends_on,
                    "timeout": call.timeout
                }
                for call in plan.tools
            ],
            "success_count": 1,
            "avg_success_rating": success_rating,
            "created_at": datetime.now().isoformat()
        }
        
        self.workflow_templates[template_id] = template
        
        # Save to disk
        with open("conductor_templates.json", 'w') as f:
            json.dump(self.workflow_templates, f, indent=2)
