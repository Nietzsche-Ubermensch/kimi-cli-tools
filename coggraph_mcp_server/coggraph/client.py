"""
CogGraph Client

High-level client for interacting with the CogGraph MCP Server.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ReasoningResult:
    """Result from a reasoning session."""
    session_id: str
    steps: List[Dict[str, Any]]
    decision_id: Optional[str] = None
    synthesis: Optional[Dict] = None


class CogGraphClient:
    """
    Client for CogGraph MCP Server.
    
    Provides convenient methods for:
    - Starting reasoning sessions
    - Recording steps and decisions
    - Querying the cognitive graph
    - Synthesizing insights
    """
    
    def __init__(self, server=None):
        """
        Initialize client.
        
        Args:
            server: CogGraphServer instance (or None for standalone mode)
        """
        self.server = server
        self._active_sessions: Dict[str, Dict] = {}
    
    async def reason_with_memory(
        self,
        query: str,
        context: Optional[Dict] = None,
        steps: Optional[List[str]] = None,
        session_id: Optional[str] = None
    ) -> ReasoningResult:
        """
        Execute reasoning with memory persistence.
        
        Args:
            query: The question or problem to reason about
            context: Additional context
            steps: Pre-defined reasoning steps
            session_id: Existing session to continue
            
        Returns:
            ReasoningResult with session info
        """
        if self.server:
            result = self.server.handle_tool_call(
                "reason_with_memory",
                {
                    "query": query,
                    "context": context or {},
                    "steps": steps or [],
                    "session_id": session_id
                }
            )
            
            if "error" in result:
                raise RuntimeError(result["error"])
            
            return ReasoningResult(
                session_id=result["session_id"],
                steps=result.get("step_ids", []),
                decision_id=None
            )
        else:
            # Standalone mode - return template
            return ReasoningResult(
                session_id=session_id or "template_session",
                steps=[],
                decision_id=None
            )
    
    async def record_step(
        self,
        session_id: str,
        content: str,
        evidence_refs: Optional[List[str]] = None,
        confidence: float = 0.5
    ) -> Dict[str, Any]:
        """Record a single reasoning step."""
        if self.server:
            return self.server.engine.add_step(
                session_id=session_id,
                content=content,
                evidence_refs=evidence_refs,
                confidence=confidence
            )
        return {"step_id": "template", "step_number": 1}
    
    async def record_decision(
        self,
        session_id: str,
        decision: str,
        rationale: str,
        confidence: float = 0.5,
        external_refs: Optional[List[str]] = None
    ) -> str:
        """
        Record a decision with full context.
        
        Args:
            session_id: Session that led to this decision
            decision: The decision made
            rationale: Explanation
            confidence: Confidence level
            external_refs: External references (Linear issue, GitHub PR, etc.)
            
        Returns:
            Decision ID
        """
        if self.server:
            result = self.server.handle_tool_call(
                "record_decision",
                {
                    "session_id": session_id,
                    "decision": decision,
                    "rationale": rationale,
                    "confidence": confidence,
                    "external_refs": external_refs or []
                }
            )
            
            if "error" in result:
                raise RuntimeError(result["error"])
            
            return result["decision_id"]
        return "template_decision_id"
    
    async def synthesize_insights(
        self,
        topic: str,
        session_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Synthesize insights across sessions.
        
        Args:
            topic: Topic to synthesize
            session_ids: Optional session filter
            
        Returns:
            Synthesis results
        """
        if self.server:
            result = self.server.handle_tool_call(
                "synthesize_insights",
                {
                    "topic": topic,
                    "session_ids": session_ids
                }
            )
            
            if "error" in result:
                raise RuntimeError(result["error"])
            
            return result
        
        return {
            "topic": topic,
            "key_concepts": [],
            "supporting_evidence": []
        }
    
    async def trace_decision(self, decision_id: str) -> Dict[str, Any]:
        """
        Trace the complete reasoning path for a decision.
        
        Args:
            decision_id: Decision to trace
            
        Returns:
            Full reasoning chain
        """
        if self.server:
            result = self.server.handle_tool_call(
                "trace_decision",
                {"decision_id": decision_id}
            )
            
            if "error" in result:
                raise RuntimeError(result["error"])
            
            return result
        
        return {
            "decision_id": decision_id,
            "reasoning_chain": [],
            "supporting_evidence": []
        }
    
    async def continue_reasoning(
        self,
        session_id: str,
        new_query: Optional[str] = None
    ) -> str:
        """
        Continue a previous reasoning session.
        
        Args:
            session_id: Session to continue
            new_query: New angle or sub-question
            
        Returns:
            New session ID
        """
        if self.server:
            result = self.server.handle_tool_call(
                "continue_reasoning",
                {
                    "session_id": session_id,
                    "new_query": new_query
                }
            )
            
            if "error" in result:
                raise RuntimeError(result["error"])
            
            return result["new_session_id"]
        return "new_template_session"
    
    async def find_related_concepts(
        self,
        concept_id: str,
        max_depth: int = 2
    ) -> Dict[str, List[Dict]]:
        """
        Find semantically related concepts.
        
        Args:
            concept_id: Starting concept
            max_depth: Traversal depth
            
        Returns:
            Related concepts by relationship type
        """
        if self.server:
            result = self.server.handle_tool_call(
                "find_related_concepts",
                {
                    "concept_id": concept_id,
                    "max_depth": max_depth
                }
            )
            
            if "error" in result:
                raise RuntimeError(result["error"])
            
            return result["related_concepts"]
        return {}
    
    async def record_evidence(
        self,
        content: str,
        source: str,
        evidence_type: str = "document",
        related_concepts: Optional[List[str]] = None
    ) -> str:
        """
        Record external evidence.
        
        Args:
            content: Evidence content/summary
            source: Source URL/reference
            evidence_type: Type of evidence
            related_concepts: Related concept IDs
            
        Returns:
            Evidence ID
        """
        if self.server:
            result = self.server.handle_tool_call(
                "record_evidence",
                {
                    "content": content,
                    "source": source,
                    "evidence_type": evidence_type,
                    "related_concepts": related_concepts or []
                }
            )
            
            if "error" in result:
                raise RuntimeError(result["error"])
            
            return result["evidence_id"]
        return "template_evidence_id"
    
    async def search_graph(
        self,
        query: str,
        node_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search the cognitive graph.
        
        Args:
            query: Search query
            node_type: Filter by type
            top_k: Number of results
            
        Returns:
            Matching nodes
        """
        if self.server:
            result = self.server.handle_tool_call(
                "search_graph",
                {
                    "query": query,
                    "node_type": node_type,
                    "top_k": top_k
                }
            )
            
            if "error" in result:
                raise RuntimeError(result["error"])
            
            return result.get("results", [])
        return []
    
    async def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        if self.server:
            result = self.server.handle_tool_call("get_graph_stats", {})
            return result
        return {"total_nodes": 0, "total_edges": 0}
    
    async def get_session_report(self, session_id: str) -> Dict[str, Any]:
        """Get detailed session report."""
        if self.server:
            result = self.server.handle_tool_call(
                "get_session_status",
                {"session_id": session_id}
            )
            return result
        return {"session_id": session_id, "status": "unknown"}
