"""
Result Synthesizer

Combines multiple tool outputs into coherent, actionable responses.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .executor import ToolResult, ExecutionState
from .planner import ExecutionPlan


@dataclass
class SynthesisResult:
    """Final synthesized result."""
    summary: str
    details: Dict[str, Any]
    recommendations: List[str]
    confidence: float
    sources: List[str]
    execution_summary: Dict[str, Any]


class ResultSynthesizer:
    """
    Synthesizes tool execution results into coherent output.
    """
    
    def __init__(self):
        self.synthesis_strategies = {
            "simple_merge": self._merge_simple,
            "merge_and_prioritize": self._merge_and_prioritize,
            "diagnostic_chain": self._diagnostic_chain,
            "structured_plan": self._structured_plan,
            "evidence_summary": self._evidence_summary,
            "narrative_merge": self._narrative_merge
        }
    
    def synthesize(
        self,
        state: ExecutionState,
        plan: ExecutionPlan,
        original_intent: str
    ) -> SynthesisResult:
        """
        Synthesize execution results into final output.
        
        Args:
            state: Execution state with all results
            plan: Original execution plan
            original_intent: User's original intent
            
        Returns:
            Synthesized result
        """
        strategy = self.synthesis_strategies.get(
            plan.synthesis_strategy,
            self._merge_simple
        )
        
        return strategy(state, plan, original_intent)
    
    def _merge_simple(
        self,
        state: ExecutionState,
        plan: ExecutionPlan,
        original_intent: str
    ) -> SynthesisResult:
        """Simple merge of all tool outputs."""
        outputs = []
        sources = []
        
        for tool_name, result in state.results.items():
            if result.success:
                outputs.append({
                    "tool": tool_name,
                    "output": result.output
                })
                sources.append(tool_name)
        
        summary = self._generate_summary(outputs, original_intent)
        
        return SynthesisResult(
            summary=summary,
            details={"tool_outputs": outputs},
            recommendations=self._extract_recommendations(outputs),
            confidence=self._calculate_confidence(state),
            sources=sources,
            execution_summary=self._execution_summary(state, plan)
        )
    
    def _merge_and_prioritize(
        self,
        state: ExecutionState,
        plan: ExecutionPlan,
        original_intent: str
    ) -> SynthesisResult:
        """Merge outputs with source prioritization."""
        # Prioritize sources (e.g., Perplexity over Brave)
        priority_order = ["perplexity", "firecrawl", "brave", "github", "context7"]
        
        sorted_results = sorted(
            state.results.items(),
            key=lambda x: priority_order.index(x[0])
            if x[0] in priority_order else 999
        )
        
        primary_output = None
        supporting_outputs = []
        
        for tool_name, result in sorted_results:
            if result.success:
                if primary_output is None:
                    primary_output = result.output
                else:
                    supporting_outputs.append({
                        "tool": tool_name,
                        "output": result.output
                    })
        
        summary = self._generate_enhanced_summary(
            primary_output,
            supporting_outputs,
            original_intent
        )
        
        return SynthesisResult(
            summary=summary,
            details={
                "primary_output": primary_output,
                "supporting_outputs": supporting_outputs
            },
            recommendations=self._extract_recommendations_from_hierarchy(
                primary_output,
                supporting_outputs
            ),
            confidence=self._calculate_confidence(state),
            sources=[r[0] for r in sorted_results if r[1].success],
            execution_summary=self._execution_summary(state, plan)
        )
    
    def _diagnostic_chain(
        self,
        state: ExecutionState,
        plan: ExecutionPlan,
        original_intent: str
    ) -> SynthesisResult:
        """Chain diagnostic findings into actionable steps."""
        findings = []
        steps = []
        
        for tool_name, result in state.results.items():
            if not result.success:
                continue
                
            output = result.output
            
            if tool_name == "chrome":
                findings.append({
                    "source": "Browser inspection",
                    "finding": self._extract_error_info(output)
                })
            elif tool_name == "github":
                findings.append({
                    "source": "Code search",
                    "finding": self._extract_code_matches(output)
                })
            elif tool_name == "perplexity":
                findings.append({
                    "source": "Research",
                    "finding": output
                })
        
        # Build diagnostic chain
        diagnostic = self._build_diagnostic(findings)
        steps = self._derive_fix_steps(findings)
        
        summary = f"## Diagnosis\n\n{diagnostic}\n\n## Fix Steps\n\n" + \
                  "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
        
        return SynthesisResult(
            summary=summary,
            details={"findings": findings, "steps": steps},
            recommendations=steps,
            confidence=self._calculate_confidence(state),
            sources=list(state.results.keys()),
            execution_summary=self._execution_summary(state, plan)
        )
    
    def _structured_plan(
        self,
        state: ExecutionState,
        plan: ExecutionPlan,
        original_intent: str
    ) -> SynthesisResult:
        """Structure implementation plan from tool outputs."""
        research = None
        code_examples = None
        api_docs = None
        
        for tool_name, result in state.results.items():
            if not result.success:
                continue
                
            if tool_name == "perplexity":
                research = result.output
            elif tool_name == "github":
                code_examples = self._extract_code_examples(result.output)
            elif tool_name == "context7":
                api_docs = result.output
        
        implementation_plan = self._build_implementation_plan(
            original_intent,
            research,
            code_examples,
            api_docs
        )
        
        return SynthesisResult(
            summary=implementation_plan["summary"],
            details={
                "phases": implementation_plan["phases"],
                "code_examples": code_examples,
                "api_references": api_docs
            },
            recommendations=implementation_plan["next_steps"],
            confidence=self._calculate_confidence(state),
            sources=list(state.results.keys()),
            execution_summary=self._execution_summary(state, plan)
        )
    
    def _evidence_summary(
        self,
        state: ExecutionState,
        plan: ExecutionPlan,
        original_intent: str
    ) -> SynthesisResult:
        """Summarize evidence from investigation."""
        evidence = []
        
        for tool_name, result in state.results.items():
            if result.success:
                evidence.append({
                    "source": tool_name,
                    "data": result.output,
                    "reliability": self._assess_reliability(tool_name)
                })
        
        # Weight by reliability
        weighted_summary = self._create_weighted_summary(evidence)
        
        return SynthesisResult(
            summary=weighted_summary["summary"],
            details={"evidence": evidence, "analysis": weighted_summary["analysis"]},
            recommendations=weighted_summary["recommendations"],
            confidence=self._calculate_confidence(state),
            sources=list(state.results.keys()),
            execution_summary=self._execution_summary(state, plan)
        )
    
    def _narrative_merge(
        self,
        state: ExecutionState,
        plan: ExecutionPlan,
        original_intent: str
    ) -> SynthesisResult:
        """Merge into narrative documentation format."""
        sections = []
        
        for tool_name, result in state.results.items():
            if result.success:
                section = self._format_as_section(tool_name, result.output)
                sections.append(section)
        
        narrative = self._weave_narrative(sections, original_intent)
        
        return SynthesisResult(
            summary=narrative["summary"],
            details={
                "narrative": narrative["full_text"],
                "sections": sections
            },
            recommendations=narrative["key_points"],
            confidence=self._calculate_confidence(state),
            sources=list(state.results.keys()),
            execution_summary=self._execution_summary(state, plan)
        )
    
    # Helper methods
    
    def _generate_summary(
        self,
        outputs: List[Dict],
        intent: str
    ) -> str:
        """Generate a natural language summary."""
        tool_names = [o["tool"] for o in outputs]
        summary_parts = [
            f"Based on analysis from {', '.join(tool_names)},",
            f"here are the findings for: *{intent}*\n"
        ]
        
        for output in outputs:
            content = output["output"]
            if isinstance(content, str):
                summary_parts.append(f"\n**{output['tool'].title()}**: {content[:200]}...")
            elif isinstance(content, dict) and "content" in content:
                summary_parts.append(f"\n**{output['tool'].title()}**: {content['content'][:200]}...")
        
        return "\n".join(summary_parts)
    
    def _generate_enhanced_summary(
        self,
        primary: Any,
        supporting: List[Dict],
        intent: str
    ) -> str:
        """Generate summary with primary and supporting sources."""
        summary = f"## Analysis: {intent}\n\n"
        
        if primary:
            summary += "### Primary Findings\n\n"
            if isinstance(primary, str):
                summary += primary[:500] + "\n\n"
            else:
                summary += str(primary)[:500] + "\n\n"
        
        if supporting:
            summary += "### Supporting Information\n\n"
            for sup in supporting[:3]:  # Limit to top 3
                summary += f"- **{sup['tool'].title()}**: "
                if isinstance(sup["output"], str):
                    summary += sup["output"][:150] + "...\n"
                else:
                    summary += str(sup["output"])[:150] + "...\n"
        
        return summary
    
    def _extract_recommendations(self, outputs: List[Dict]) -> List[str]:
        """Extract actionable recommendations."""
        recommendations = []
        
        for output in outputs:
            content = output.get("output", "")
            if isinstance(content, str):
                # Look for action keywords
                if any(kw in content.lower() for kw in ["should", "recommend", "consider"]):
                    # Extract sentences with recommendations
                    sentences = content.split(".")
                    for sent in sentences:
                        if any(kw in sent.lower() for kw in ["should", "recommend"]):
                            recommendations.append(sent.strip())
        
        return list(set(recommendations))[:5]  # Deduplicate and limit
    
    def _calculate_confidence(self, state: ExecutionState) -> float:
        """Calculate overall confidence from execution state."""
        if not state.results:
            return 0.0
        
        success_count = sum(1 for r in state.results.values() if r.success)
        return success_count / len(state.results)
    
    def _execution_summary(
        self,
        state: ExecutionState,
        plan: ExecutionPlan
    ) -> Dict[str, Any]:
        """Generate execution summary."""
        total_tools = len(plan.tools)
        successful_tools = sum(1 for r in state.results.values() if r.success)
        
        return {
            "total_tools": total_tools,
            "successful": successful_tools,
            "failed": total_tools - successful_tools,
            "duration": self._calculate_duration(state),
            "tools_used": list(state.results.keys())
        }
    
    def _calculate_duration(self, state: ExecutionState) -> int:
        """Calculate execution duration."""
        if state.start_time and state.end_time:
            start = datetime.fromisoformat(state.start_time)
            end = datetime.fromisoformat(state.end_time)
            return int((end - start).total_seconds())
        return 0
    
    def _extract_error_info(self, output: Any) -> str:
        """Extract error information from Chrome output."""
        if isinstance(output, dict):
            return output.get("error", str(output))
        return str(output)
    
    def _extract_code_matches(self, output: Any) -> str:
        """Extract code matches from GitHub search."""
        if isinstance(output, dict):
            items = output.get("items", [])
            return f"Found {len(items)} relevant code matches"
        return str(output)
    
    def _build_diagnostic(self, findings: List[Dict]) -> str:
        """Build diagnostic from findings."""
        parts = []
        for finding in findings:
            parts.append(f"**{finding['source']}**: {finding['finding']}")
        return "\n\n".join(parts)
    
    def _derive_fix_steps(self, findings: List[Dict]) -> List[str]:
        """Derive fix steps from diagnostic findings."""
        steps = []
        
        for finding in findings:
            finding_text = str(finding.get("finding", "")).lower()
            
            if "error" in finding_text or "failed" in finding_text:
                steps.append(f"Address {finding['source'].lower()} issue")
            if "deprecated" in finding_text:
                steps.append("Update deprecated dependencies")
            if "missing" in finding_text:
                steps.append("Install missing dependencies")
        
        return steps if steps else ["Review diagnostic findings"]
    
    def _extract_code_examples(self, output: Any) -> List[Dict]:
        """Extract code examples from GitHub output."""
        if isinstance(output, dict):
            items = output.get("items", [])
            return [
                {
                    "repo": item.get("repository", {}).get("full_name"),
                    "path": item.get("path"),
                    "url": item.get("html_url")
                }
                for item in items[:5]
            ]
        return []
    
    def _build_implementation_plan(
        self,
        intent: str,
        research: Any,
        code_examples: List[Dict],
        api_docs: Any
    ) -> Dict:
        """Build structured implementation plan."""
        phases = [
            {"name": "Research & Understanding", "status": "completed", "output": research},
            {"name": "Code Reference", "status": "completed", "output": code_examples},
            {"name": "API Review", "status": "completed", "output": api_docs},
            {"name": "Implementation", "status": "pending"},
            {"name": "Testing", "status": "pending"}
        ]
        
        return {
            "summary": f"Implementation plan for: {intent}",
            "phases": phases,
            "next_steps": [
                "Review gathered research and code examples",
                "Set up development environment",
                "Implement core functionality",
                "Test and iterate"
            ]
        }
    
    def _assess_reliability(self, tool_name: str) -> float:
        """Assess reliability of a tool."""
        reliability_map = {
            "perplexity": 0.9,
            "github": 0.95,
            "context7": 0.9,
            "firecrawl": 0.85,
            "brave": 0.8,
            "chrome": 0.9,
            "linear": 0.95,
            "playwright": 0.9
        }
        return reliability_map.get(tool_name, 0.8)
    
    def _create_weighted_summary(self, evidence: List[Dict]) -> Dict:
        """Create summary weighted by reliability."""
        total_weight = sum(e["reliability"] for e in evidence)
        
        return {
            "summary": f"Based on {len(evidence)} sources with {total_weight:.1f} cumulative reliability",
            "analysis": {e["source"]: e["data"] for e in evidence},
            "recommendations": [f"Consider {e['source']} findings" for e in evidence[:3]]
        }
    
    def _format_as_section(self, tool_name: str, output: Any) -> Dict:
        """Format tool output as a documentation section."""
        return {
            "title": tool_name.replace("_", " ").title(),
            "content": output if isinstance(output, str) else json.dumps(output, indent=2)
        }
    
    def _weave_narrative(self, sections: List[Dict], intent: str) -> Dict:
        """Weave sections into narrative."""
        full_text = f"# {intent}\n\n"
        key_points = []
        
        for section in sections:
            full_text += f"## {section['title']}\n\n{section['content']}\n\n"
            # Extract key point
            lines = section["content"].split("\n")
            if lines:
                key_points.append(lines[0][:100])
        
        return {
            "summary": f"Complete documentation for: {intent}",
            "full_text": full_text,
            "key_points": key_points[:5]
        }
    
    def _extract_recommendations_from_hierarchy(
        self,
        primary: Any,
        supporting: List[Dict]
    ) -> List[str]:
        """Extract recommendations from hierarchical results."""
        recommendations = []
        
        if primary and isinstance(primary, str):
            recommendations.append(primary[:200])
        
        for sup in supporting:
            if isinstance(sup.get("output"), str):
                recommendations.append(f"{sup['tool']}: {sup['output'][:150]}")
        
        return recommendations[:5]
