"""
CogGraph MCP Server Implementation

Exposes cognitive graph capabilities through the Model Context Protocol.
"""

import json
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

from .graph import CognitiveGraph
from .reasoning import ReasoningEngine


class CogGraphServer:
    """
    MCP Server for CogGraph - Cognitive Graph with Persistent Reasoning.
    
    Tools exposed:
    - reason_with_memory: Execute sequential thinking with persistence
    - synthesize_insights: Query across reasoning sessions
    - trace_decision: Reconstruct decision rationale
    - continue_reasoning: Resume previous sessions
    - find_related_concepts: Discover semantic connections
    - record_evidence: Store external evidence
    - record_decision: Capture decisions with full context
    - get_session_status: Check reasoning session state
    """
    
    def __init__(self, storage_path: str = "cognitive_graph.json"):
        self.graph = CognitiveGraph(storage_path)
        self.engine = ReasoningEngine(self.graph)
        self.server_info = {
            "name": "coggraph",
            "version": "1.0.0",
            "description": "Cognitive Graph Server for Persistent Reasoning Context"
        }
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return MCP server capabilities."""
        return {
            "tools": [
                {
                    "name": "reason_with_memory",
                    "description": "Execute sequential reasoning while persisting each step to the cognitive graph. Maintains context across sessions.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The question or problem to reason about"},
                            "context": {"type": "object", "description": "Additional context (facts, constraints)"},
                            "steps": {"type": "array", "items": {"type": "string"}, "description": "Pre-defined reasoning steps (optional)"},
                            "session_id": {"type": "string", "description": "Existing session ID to continue (optional)"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "synthesize_insights",
                    "description": "Query the cognitive graph to synthesize insights across multiple research sessions, identifying patterns and contradictions.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string", "description": "Topic to synthesize insights about"},
                            "session_ids": {"type": "array", "items": {"type": "string"}, "description": "Restrict to specific sessions (optional)"},
                            "min_relevance": {"type": "number", "description": "Minimum relevance threshold (0-1)"}
                        },
                        "required": ["topic"]
                    }
                },
                {
                    "name": "trace_decision",
                    "description": "Trace the complete reasoning path from a decision back to its evidence sources and intermediate steps.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "decision_id": {"type": "string", "description": "ID of the decision node to trace"}
                        },
                        "required": ["decision_id"]
                    }
                },
                {
                    "name": "continue_reasoning",
                    "description": "Resume a previous reasoning session, maintaining full context from earlier steps.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session ID to continue"},
                            "new_query": {"type": "string", "description": "New angle or sub-question (optional)"}
                        },
                        "required": ["session_id"]
                    }
                },
                {
                    "name": "find_related_concepts",
                    "description": "Discover semantically related concepts in the cognitive graph, even if never explicitly linked.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "concept_id": {"type": "string", "description": "Concept node ID to start from"},
                            "max_depth": {"type": "integer", "description": "Maximum traversal depth (default 2)"},
                            "relationship_types": {"type": "array", "items": {"type": "string"}, "description": "Filter by relationship types"}
                        },
                        "required": ["concept_id"]
                    }
                },
                {
                    "name": "record_evidence",
                    "description": "Store external evidence (URLs, documents, code) in the cognitive graph for later reference.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "Evidence content or summary"},
                            "source": {"type": "string", "description": "Source URL or reference"},
                            "evidence_type": {"type": "string", "description": "Type: url, document, code, observation"},
                            "metadata": {"type": "object", "description": "Additional metadata"},
                            "related_concepts": {"type": "array", "items": {"type": "string"}, "description": "Related concept IDs"}
                        },
                        "required": ["content", "source"]
                    }
                },
                {
                    "name": "record_decision",
                    "description": "Record a decision with its full reasoning context, enabling future traceability.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Reasoning session that led to this decision"},
                            "decision": {"type": "string", "description": "The decision made"},
                            "rationale": {"type": "string", "description": "Explanation of why this decision was made"},
                            "confidence": {"type": "number", "description": "Confidence level 0-1 (default 0.5)"},
                            "external_refs": {"type": "array", "items": {"type": "string"}, "description": "External references (e.g., Linear issue, GitHub PR)"}
                        },
                        "required": ["session_id", "decision", "rationale"]
                    }
                },
                {
                    "name": "get_session_status",
                    "description": "Get the current status and summary of a reasoning session.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "Session ID to check"}
                        },
                        "required": ["session_id"]
                    }
                },
                {
                    "name": "search_graph",
                    "description": "Search the cognitive graph for concepts, evidence, or decisions matching a query.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "node_type": {"type": "string", "description": "Filter by node type (optional)"},
                            "top_k": {"type": "integer", "description": "Number of results (default 5)"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_graph_stats",
                    "description": "Get statistics about the cognitive graph.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    
    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP tool call."""
        try:
            if tool_name == "reason_with_memory":
                return self._tool_reason_with_memory(arguments)
            elif tool_name == "synthesize_insights":
                return self._tool_synthesize_insights(arguments)
            elif tool_name == "trace_decision":
                return self._tool_trace_decision(arguments)
            elif tool_name == "continue_reasoning":
                return self._tool_continue_reasoning(arguments)
            elif tool_name == "find_related_concepts":
                return self._tool_find_related_concepts(arguments)
            elif tool_name == "record_evidence":
                return self._tool_record_evidence(arguments)
            elif tool_name == "record_decision":
                return self._tool_record_decision(arguments)
            elif tool_name == "get_session_status":
                return self._tool_get_session_status(arguments)
            elif tool_name == "search_graph":
                return self._tool_search_graph(arguments)
            elif tool_name == "get_graph_stats":
                return self._tool_get_graph_stats()
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_reason_with_memory(self, args: Dict) -> Dict[str, Any]:
        """Execute reasoning with memory persistence."""
        query = args["query"]
        context = args.get("context", {})
        steps = args.get("steps", [])
        session_id = args.get("session_id")
        
        # Start or continue session
        if session_id and session_id in self.engine.active_sessions:
            # Continue existing
            pass
        else:
            session_id = self.engine.start_session(query, context, session_id)
        
        # Add reasoning steps
        step_results = []
        for i, step_content in enumerate(steps):
            result = self.engine.add_step(
                session_id=session_id,
                content=step_content,
                confidence=0.7 + (0.1 * i)  # Increasing confidence
            )
            step_results.append(result)
        
        # Save graph state
        self.graph.save()
        
        return {
            "session_id": session_id,
            "query": query,
            "steps_recorded": len(step_results),
            "step_ids": [r["step_id"] for r in step_results],
            "reasoning_types": list(set(r["reasoning_type"] for r in step_results)),
            "status": "success"
        }
    
    def _tool_synthesize_insights(self, args: Dict) -> Dict[str, Any]:
        """Synthesize insights across sessions."""
        topic = args["topic"]
        session_ids = args.get("session_ids")
        min_relevance = args.get("min_relevance", 0.3)
        
        synthesis = self.graph.synthesize_insights(topic, session_ids)
        
        # Filter by relevance
        for key in ["key_concepts", "supporting_evidence"]:
            if key in synthesis:
                synthesis[key] = [
                    item for item in synthesis[key]
                    if item.get("relevance", 0) >= min_relevance
                ]
        
        return synthesis
    
    def _tool_trace_decision(self, args: Dict) -> Dict[str, Any]:
        """Trace decision rationale."""
        decision_id = args["decision_id"]
        
        if decision_id not in self.graph.graph:
            return {"error": f"Decision not found: {decision_id}"}
        
        decision_data = self.graph.graph.nodes[decision_id]
        reasoning_chain = self.graph.trace_reasoning(decision_id)
        
        # Get related evidence
        evidence = []
        for step in reasoning_chain:
            for evidence_id in step.get("metadata", {}).get("evidence_refs", []):
                if evidence_id in self.graph.graph:
                    evidence.append({
                        "id": evidence_id,
                        "content": self.graph.graph.nodes[evidence_id].get("content", "")[:200]
                    })
        
        return {
            "decision_id": decision_id,
            "decision": decision_data.get("content"),
            "metadata": decision_data.get("metadata"),
            "reasoning_chain": reasoning_chain,
            "supporting_evidence": evidence,
            "total_steps": len(reasoning_chain)
        }
    
    def _tool_continue_reasoning(self, args: Dict) -> Dict[str, Any]:
        """Continue a reasoning session."""
        session_id = args["session_id"]
        new_query = args.get("new_query")
        
        new_session_id = self.engine.continue_session(session_id, new_query)
        
        # Save graph
        self.graph.save()
        
        return {
            "new_session_id": new_session_id,
            "continues_from": session_id,
            "new_query": new_query or "Continued session",
            "status": "active"
        }
    
    def _tool_find_related_concepts(self, args: Dict) -> Dict[str, Any]:
        """Find related concepts in the graph."""
        concept_id = args["concept_id"]
        max_depth = args.get("max_depth", 2)
        relationship_types = args.get("relationship_types")
        
        related = self.graph.get_related_concepts(concept_id, max_depth)
        
        # Filter by relationship types if specified
        if relationship_types:
            related = {
                k: v for k, v in related.items()
                if k in relationship_types
            }
        
        return {
            "concept_id": concept_id,
            "max_depth": max_depth,
            "related_concepts": related,
            "total_related": sum(len(v) for v in related.values())
        }
    
    def _tool_record_evidence(self, args: Dict) -> Dict[str, Any]:
        """Record external evidence."""
        content = args["content"]
        source = args["source"]
        evidence_type = args.get("evidence_type", "document")
        metadata = args.get("metadata", {})
        related_concepts = args.get("related_concepts", [])
        
        evidence_id = self.graph.add_node(
            node_type="evidence",
            content=content,
            metadata={
                "source": source,
                "evidence_type": evidence_type,
                **metadata
            }
        )
        
        # Link to related concepts
        for concept_id in related_concepts:
            if concept_id in self.graph.graph:
                self.graph.add_edge(
                    source=evidence_id,
                    target=concept_id,
                    edge_type="supports",
                    weight=0.8
                )
        
        self.graph.save()
        
        return {
            "evidence_id": evidence_id,
            "source": source,
            "evidence_type": evidence_type,
            "linked_concepts": len(related_concepts)
        }
    
    def _tool_record_decision(self, args: Dict) -> Dict[str, Any]:
        """Record a decision with full context."""
        session_id = args["session_id"]
        decision = args["decision"]
        rationale = args["rationale"]
        confidence = args.get("confidence", 0.5)
        external_refs = args.get("external_refs", [])
        
        decision_id = self.engine.record_decision(
            session_id=session_id,
            decision=decision,
            rationale=rationale,
            confidence=confidence
        )
        
        # Add external references
        for ref in external_refs:
            ref_id = self.graph.add_node(
                node_type="evidence",
                content=f"External reference: {ref}",
                metadata={"reference": ref, "type": "external"}
            )
            self.graph.add_edge(
                source=decision_id,
                target=ref_id,
                edge_type="evidence_for",
                weight=1.0
            )
        
        self.graph.save()
        
        return {
            "decision_id": decision_id,
            "session_id": session_id,
            "decision": decision,
            "confidence": confidence,
            "external_refs_recorded": len(external_refs)
        }
    
    def _tool_get_session_status(self, args: Dict) -> Dict[str, Any]:
        """Get session status."""
        session_id = args["session_id"]
        
        summary = self.engine.get_session_summary(session_id)
        quality = self.engine.analyze_reasoning_quality(session_id)
        
        return {
            **summary,
            "quality_analysis": quality
        }
    
    def _tool_search_graph(self, args: Dict) -> Dict[str, Any]:
        """Search the cognitive graph."""
        query = args["query"]
        node_type = args.get("node_type")
        top_k = args.get("top_k", 5)
        
        results = self.graph.find_similar(query, node_type, top_k)
        
        detailed_results = []
        for node_id, score in results:
            node_data = self.graph.graph.nodes[node_id]
            detailed_results.append({
                "id": node_id,
                "type": node_data.get("type"),
                "content": node_data.get("content", "")[:200],
                "relevance_score": round(score, 3),
                "created_at": node_data.get("created_at")
            })
        
        return {
            "query": query,
            "results": detailed_results,
            "total_found": len(detailed_results)
        }
    
    def _tool_get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return self.graph.get_stats()
    
    def run_stdio(self):
        """Run the server using stdio transport (MCP standard)."""
        for line in sys.stdin:
            try:
                request = json.loads(line)
                
                if request.get("method") == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": self.get_capabilities(),
                            "serverInfo": self.server_info
                        }
                    }
                    print(json.dumps(response), flush=True)
                
                elif request.get("method") == "tools/call":
                    params = request.get("params", {})
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    result = self.handle_tool_call(tool_name, arguments)
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, indent=2)
                                }
                            ]
                        }
                    }
                    print(json.dumps(response), flush=True)
                
                elif request.get("method") == "tools/list":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": self.get_capabilities()
                    }
                    print(json.dumps(response), flush=True)
                    
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(error_response), flush=True)


def main():
    """Entry point for the MCP server."""
    server = CogGraphServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
