"""
Sequential Thinking Engine

Implements step-by-step reasoning with persistence to the cognitive graph.
Combines Sequential Thinking capabilities with Memory storage.
"""

import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime

from .graph import CognitiveGraph


@dataclass
class ReasoningStep:
    """A single step in a reasoning chain."""
    step_number: int
    content: str
    reasoning_type: str  # analysis, evaluation, synthesis, decision
    evidence_refs: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    confidence: float = 0.5


@dataclass
class ReasoningSession:
    """A complete reasoning session."""
    session_id: str
    query: str
    context: Dict[str, Any]
    steps: List[ReasoningStep] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "active"  # active, paused, completed


class ReasoningEngine:
    """
    Sequential thinking engine with cognitive graph integration.
    
    This combines:
    - Sequential Thinking: Step-by-step reasoning
    - Memory: Persistent storage of reasoning chains
    - Fetch: Integration of external evidence
    """
    
    REASONING_PATTERNS = {
        "analysis": [
            "break down",
            "analyze",
            "examine",
            "deconstruct",
            "identify components"
        ],
        "evaluation": [
            "assess",
            "evaluate",
            "compare",
            "weigh",
            "trade-off"
        ],
        "synthesis": [
            "synthesize",
            "combine",
            "integrate",
            "connect",
            "pattern"
        ],
        "decision": [
            "decide",
            "conclude",
            "recommend",
            "choose",
            "select"
        ]
    }
    
    def __init__(self, graph: CognitiveGraph):
        self.graph = graph
        self.active_sessions: Dict[str, ReasoningSession] = {}
    
    def _detect_reasoning_type(self, content: str) -> str:
        """Detect the type of reasoning in a step."""
        content_lower = content.lower()
        
        type_scores = {}
        for rtype, patterns in self.REASONING_PATTERNS.items():
            score = sum(1 for p in patterns if p in content_lower)
            type_scores[rtype] = score
        
        # Return type with highest score, default to analysis
        if max(type_scores.values()) > 0:
            return max(type_scores, key=type_scores.get)
        return "analysis"
    
    def _extract_assumptions(self, content: str) -> List[str]:
        """Extract explicit assumptions from reasoning text."""
        assumptions = []
        
        # Pattern: "assuming that...", "if we assume..."
        patterns = [
            r'assuming (?:that )?([^,.]+)',
            r'if we assume (?:that )?([^,.]+)',
            r'assumption: ([^,.]+)',
            r'presuppose[s]? (?:that )?([^,.]+)',
            r'given (?:that )?([^,.]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            assumptions.extend(matches)
        
        return [a.strip() for a in assumptions if len(a.strip()) > 10]
    
    def start_session(
        self,
        query: str,
        context: Optional[Dict] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Start a new reasoning session.
        
        Args:
            query: The question or problem to reason about
            context: Additional context (facts, constraints, etc.)
            session_id: Optional explicit session ID
            
        Returns:
            Session ID
        """
        session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = ReasoningSession(
            session_id=session_id,
            query=query,
            context=context or {},
            steps=[]
        )
        
        self.active_sessions[session_id] = session
        
        # Add session node to graph
        self.graph.add_node(
            node_type="session",
            content=query,
            metadata={
                "session_id": session_id,
                "context": context,
                "status": "active"
            },
            node_id=session_id
        )
        
        return session_id
    
    def add_step(
        self,
        session_id: str,
        content: str,
        evidence_refs: Optional[List[str]] = None,
        confidence: float = 0.5
    ) -> Dict[str, Any]:
        """
        Add a reasoning step to the session.
        
        Args:
            session_id: Active session ID
            content: Step content
            evidence_refs: References to evidence nodes
            confidence: Confidence level (0-1)
            
        Returns:
            Step information including generated ID
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = self.active_sessions[session_id]
        step_number = len(session.steps) + 1
        
        # Detect reasoning type and assumptions
        reasoning_type = self._detect_reasoning_type(content)
        assumptions = self._extract_assumptions(content)
        
        step = ReasoningStep(
            step_number=step_number,
            content=content,
            reasoning_type=reasoning_type,
            evidence_refs=evidence_refs or [],
            assumptions=assumptions,
            confidence=confidence
        )
        
        session.steps.append(step)
        
        # Add to cognitive graph
        step_id = self.graph.add_node(
            node_type="reasoning_step",
            content=content,
            metadata={
                "session_id": session_id,
                "step_number": step_number,
                "reasoning_type": reasoning_type,
                "assumptions": assumptions,
                "confidence": confidence,
                "evidence_refs": evidence_refs
            }
        )
        
        # Link to session
        self.graph.add_edge(
            source=session_id,
            target=step_id,
            edge_type="part_of",
            weight=1.0
        )
        
        # Link to previous step if exists
        if step_number > 1:
            prev_step = session.steps[step_number - 2]
            # Find the previous step's node ID
            for node_id, data in self.graph.graph.nodes(data=True):
                if (data.get("metadata", {}).get("session_id") == session_id and
                    data.get("metadata", {}).get("step_number") == step_number - 1):
                    self.graph.add_edge(
                        source=node_id,
                        target=step_id,
                        edge_type="led_to",
                        weight=confidence
                    )
                    break
        
        # Link to evidence
        for evidence_id in (evidence_refs or []):
            if evidence_id in self.graph.graph:
                self.graph.add_edge(
                    source=step_id,
                    target=evidence_id,
                    edge_type="evidence_for",
                    weight=0.9
                )
        
        return {
            "step_id": step_id,
            "step_number": step_number,
            "reasoning_type": reasoning_type,
            "assumptions_identified": assumptions,
            "session_id": session_id
        }
    
    def record_decision(
        self,
        session_id: str,
        decision: str,
        rationale: str,
        confidence: float = 0.5
    ) -> str:
        """
        Record a decision that concludes a reasoning session.
        
        Args:
            session_id: Active session ID
            decision: The decision made
            rationale: Why this decision was made
            confidence: Confidence in the decision
            
        Returns:
            Decision node ID
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = self.active_sessions[session_id]
        
        # Add decision node
        decision_id = self.graph.add_node(
            node_type="decision",
            content=decision,
            metadata={
                "session_id": session_id,
                "rationale": rationale,
                "confidence": confidence,
                "query": session.query,
                "num_steps": len(session.steps)
            }
        )
        
        # Link from all reasoning steps
        for step in session.steps:
            # Find step node
            for node_id, data in self.graph.graph.nodes(data=True):
                if (data.get("metadata", {}).get("session_id") == session_id and
                    data.get("metadata", {}).get("step_number") == step.step_number):
                    self.graph.add_edge(
                        source=node_id,
                        target=decision_id,
                        edge_type="reasoned_from",
                        weight=step.confidence
                    )
                    break
        
        # Link from session
        self.graph.add_edge(
            source=session_id,
            target=decision_id,
            edge_type="led_to",
            weight=confidence
        )
        
        # Mark session as completed
        session.status = "completed"
        if session_id in self.graph.graph:
            self.graph.graph.nodes[session_id]["metadata"]["status"] = "completed"
            self.graph.graph.nodes[session_id]["metadata"]["decision_id"] = decision_id
        
        return decision_id
    
    def continue_session(
        self,
        session_id: str,
        new_query: Optional[str] = None
    ) -> str:
        """
        Resume a previous reasoning session with full context.
        
        Args:
            session_id: Session ID to continue
            new_query: Optional new angle or sub-question
            
        Returns:
            New session ID (linked to original)
        """
        if session_id not in self.graph.graph:
            raise ValueError(f"Session not found in graph: {session_id}")
        
        old_session_data = self.graph.graph.nodes[session_id]
        old_context = old_session_data.get("metadata", {}).get("context", {})
        old_query = old_session_data.get("content", "")
        
        # Create new session with reference to old
        new_query = new_query or f"Continue: {old_query}"
        new_session_id = self.start_session(
            query=new_query,
            context={
                **old_context,
                "continues_from": session_id,
                "original_query": old_query
            }
        )
        
        # Link sessions
        self.graph.add_edge(
            source=session_id,
            target=new_session_id,
            edge_type="supersedes",
            weight=1.0,
            metadata={"relationship": "continuation"}
        )
        
        return new_session_id
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of a reasoning session."""
        if session_id not in self.active_sessions:
            return {"error": "Session not found in active sessions"}
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "query": session.query,
            "status": session.status,
            "num_steps": len(session.steps),
            "steps": [
                {
                    "number": s.step_number,
                    "type": s.reasoning_type,
                    "content": s.content[:100],
                    "confidence": s.confidence
                }
                for s in session.steps
            ],
            "key_assumptions": list(set(
                ass for step in session.steps for ass in step.assumptions
            ))
        }
    
    def analyze_reasoning_quality(self, session_id: str) -> Dict[str, Any]:
        """
        Analyze the quality of reasoning in a session.
        
        Checks for:
        - Assumption coverage
        - Evidence support
        - Reasoning type diversity
        - Confidence consistency
        """
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        
        # Analyze reasoning type distribution
        type_counts = {}
        for step in session.steps:
            type_counts[step.reasoning_type] = type_counts.get(step.reasoning_type, 0) + 1
        
        # Check for evidence support
        steps_with_evidence = sum(
            1 for step in session.steps if step.evidence_refs
        )
        
        # Check confidence trend
        confidences = [step.confidence for step in session.steps]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Collect all assumptions
        all_assumptions = set()
        for step in session.steps:
            all_assumptions.update(step.assumptions)
        
        return {
            "total_steps": len(session.steps),
            "reasoning_type_distribution": type_counts,
            "steps_with_evidence": f"{steps_with_evidence}/{len(session.steps)}",
            "average_confidence": round(avg_confidence, 2),
            "explicit_assumptions": len(all_assumptions),
            "quality_score": self._calculate_quality_score(session)
        }
    
    def _calculate_quality_score(self, session: ReasoningSession) -> float:
        """Calculate an overall quality score for the reasoning."""
        if not session.steps:
            return 0.0
        
        scores = []
        
        # Diversity of reasoning types (max 0.3)
        types_used = len(set(s.reasoning_type for s in session.steps))
        scores.append(min(types_used / 3, 1.0) * 0.3)
        
        # Evidence support (max 0.3)
        evidence_ratio = sum(1 for s in session.steps if s.evidence_refs) / len(session.steps)
        scores.append(evidence_ratio * 0.3)
        
        # Confidence trend (max 0.2)
        # Ideally confidence should increase or stay stable
        confidences = [s.confidence for s in session.steps]
        if len(confidences) > 1:
            trend = sum(confidences[i] >= confidences[i-1] 
                       for i in range(1, len(confidences))) / (len(confidences) - 1)
            scores.append(trend * 0.2)
        else:
            scores.append(0.1)
        
        # Explicit assumptions (max 0.2)
        has_assumptions = any(s.assumptions for s in session.steps)
        scores.append(0.2 if has_assumptions else 0.0)
        
        return round(sum(scores), 2)
