"""
Cognitive Graph Implementation

A graph-based knowledge store that persists concepts, reasoning chains,
evidence, and their relationships over time.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Node:
    """Base node in the cognitive graph."""
    id: str
    type: str  # concept, reasoning_step, evidence, decision, session
    content: str
    created_at: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class Edge:
    """Relationship between nodes."""
    source: str
    target: str
    type: str  # supports, contradicts, enables, led_to, part_of
    weight: float
    created_at: str
    metadata: Dict[str, Any]


class CognitiveGraph:
    """
    Persistent cognitive graph for storing reasoning context.
    
    Combines capabilities from:
    - Memory Server: Graph storage and retrieval
    - Fetch: Content integration
    - Sequential Thinking: Reasoning chain preservation
    """
    
    NODE_TYPES = {"concept", "reasoning_step", "evidence", "decision", "session", "query"}
    EDGE_TYPES = {
        "supports", "contradicts", "enables", "led_to", "part_of",
        "reasoned_from", "evidence_for", "related_to", "supersedes"
    }
    
    def __init__(self, storage_path: str = "cognitive_graph.json"):
        self.graph = nx.DiGraph()
        self.storage_path = Path(storage_path)
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self._embeddings_cache: Dict[str, np.ndarray] = {}
        
        # Load existing graph if present
        if self.storage_path.exists():
            self.load()
    
    def _generate_id(self, content: str, node_type: str) -> str:
        """Generate unique ID for a node."""
        hash_input = f"{node_type}:{content}:{datetime.now().isoformat()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def _compute_embedding(self, text: str) -> np.ndarray:
        """Compute embedding for semantic search."""
        try:
            # Simple TF-IDF based embedding
            vectors = self.vectorizer.fit_transform([text])
            return vectors[0].toarray()[0]
        except:
            # Fallback to simple word frequency
            words = text.lower().split()
            unique_words = list(set(words))
            return np.array([words.count(w) for w in unique_words[:100]])
    
    def add_node(
        self,
        node_type: str,
        content: str,
        metadata: Optional[Dict] = None,
        node_id: Optional[str] = None
    ) -> str:
        """
        Add a node to the cognitive graph.
        
        Args:
            node_type: Type of node (concept, reasoning_step, etc.)
            content: Node content/text
            metadata: Additional metadata
            node_id: Optional explicit ID
            
        Returns:
            Node ID
        """
        if node_type not in self.NODE_TYPES:
            raise ValueError(f"Unknown node type: {node_type}")
        
        node_id = node_id or self._generate_id(content, node_type)
        
        # Compute embedding for semantic search
        embedding = self._compute_embedding(content).tolist()
        
        node = Node(
            id=node_id,
            type=node_type,
            content=content,
            created_at=datetime.now().isoformat(),
            metadata=metadata or {},
            embedding=embedding
        )
        
        # Add to NetworkX graph
        self.graph.add_node(
            node_id,
            **asdict(node)
        )
        
        self._embeddings_cache[node_id] = np.array(embedding)
        
        return node_id
    
    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: str,
        weight: float = 1.0,
        metadata: Optional[Dict] = None
    ) -> None:
        """Add a relationship between nodes."""
        if edge_type not in self.EDGE_TYPES:
            raise ValueError(f"Unknown edge type: {edge_type}")
        
        if source not in self.graph or target not in self.graph:
            raise ValueError(f"Source or target node not found: {source} -> {target}")
        
        edge = Edge(
            source=source,
            target=target,
            type=edge_type,
            weight=weight,
            created_at=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        self.graph.add_edge(source, target, **asdict(edge))
    
    def find_similar(
        self,
        query: str,
        node_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find semantically similar nodes using embeddings.
        
        Args:
            query: Search query
            node_type: Filter by node type
            top_k: Number of results
            
        Returns:
            List of (node_id, similarity_score) tuples
        """
        query_embedding = self._compute_embedding(query)
        
        candidates = []
        for node_id, data in self.graph.nodes(data=True):
            if node_type and data.get("type") != node_type:
                continue
            
            node_embedding = self._embeddings_cache.get(node_id)
            if node_embedding is None and "embedding" in data:
                node_embedding = np.array(data["embedding"])
                self._embeddings_cache[node_id] = node_embedding
            
            if node_embedding is not None:
                # Ensure same dimensionality
                min_dim = min(len(query_embedding), len(node_embedding))
                q_emb = query_embedding[:min_dim].reshape(1, -1)
                n_emb = node_embedding[:min_dim].reshape(1, -1)
                
                if q_emb.shape[1] > 0 and n_emb.shape[1] > 0:
                    similarity = cosine_similarity(q_emb, n_emb)[0][0]
                    candidates.append((node_id, float(similarity)))
        
        # Sort by similarity and return top_k
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:top_k]
    
    def trace_reasoning(self, decision_id: str) -> List[Dict]:
        """
        Trace the complete reasoning path leading to a decision.
        
        Args:
            decision_id: ID of the decision node
            
        Returns:
            List of reasoning steps in chronological order
        """
        if decision_id not in self.graph:
            return []
        
        # Find all paths leading to this decision
        reasoning_chain = []
        
        # Get immediate reasoning steps
        for predecessor in self.graph.predecessors(decision_id):
            edge_data = self.graph.get_edge_data(predecessor, decision_id)
            if edge_data and edge_data.get("type") == "led_to":
                node_data = self.graph.nodes[predecessor]
                reasoning_chain.append({
                    "step_id": predecessor,
                    "content": node_data.get("content", ""),
                    "type": node_data.get("type"),
                    "metadata": node_data.get("metadata", {})
                })
        
        # Sort by creation time if available
        reasoning_chain.sort(
            key=lambda x: x.get("metadata", {}).get("step_number", 0)
        )
        
        return reasoning_chain
    
    def get_related_concepts(
        self,
        concept_id: str,
        max_depth: int = 2
    ) -> Dict[str, List[Dict]]:
        """
        Find concepts related to a given concept.
        
        Args:
            concept_id: Starting concept
            max_depth: Maximum traversal depth
            
        Returns:
            Dictionary mapping relationship types to related concepts
        """
        if concept_id not in self.graph:
            return {}
        
        related = {
            "supports": [],
            "contradicts": [],
            "enables": [],
            "related": []
        }
        
        # BFS traversal
        visited = {concept_id}
        queue = [(concept_id, 0)]
        
        while queue:
            current_id, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            
            for neighbor in self.graph.neighbors(current_id):
                if neighbor in visited:
                    continue
                
                edge_data = self.graph.get_edge_data(current_id, neighbor)
                edge_type = edge_data.get("type", "related")
                
                node_data = self.graph.nodes[neighbor]
                concept_info = {
                    "id": neighbor,
                    "content": node_data.get("content", ""),
                    "type": node_data.get("type"),
                    "relationship": edge_type,
                    "depth": depth + 1
                }
                
                if edge_type in related:
                    related[edge_type].append(concept_info)
                else:
                    related["related"].append(concept_info)
                
                visited.add(neighbor)
                queue.append((neighbor, depth + 1))
        
        return related
    
    def synthesize_insights(
        self,
        topic: str,
        session_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Synthesize insights across multiple sessions or the entire graph.
        
        Args:
            topic: Topic to synthesize
            session_ids: Optional list of session IDs to restrict to
            
        Returns:
            Synthesis results with key insights and supporting evidence
        """
        # Find relevant nodes
        similar_nodes = self.find_similar(topic, top_k=20)
        
        if session_ids:
            # Filter to specific sessions
            filtered_nodes = []
            for node_id, score in similar_nodes:
                node_data = self.graph.nodes[node_id]
                if node_data.get("metadata", {}).get("session_id") in session_ids:
                    filtered_nodes.append((node_id, score))
            similar_nodes = filtered_nodes
        
        # Collect concepts and evidence
        concepts = []
        evidence = []
        contradictions = []
        
        for node_id, score in similar_nodes:
            node_data = self.graph.nodes[node_id]
            node_type = node_data.get("type")
            content = node_data.get("content", "")
            
            entry = {
                "id": node_id,
                "content": content[:200],
                "relevance": score,
                "type": node_type
            }
            
            if node_type == "concept":
                concepts.append(entry)
            elif node_type == "evidence":
                evidence.append(entry)
            elif node_type == "reasoning_step":
                # Check for contradictions
                for pred in self.graph.predecessors(node_id):
                    edge_data = self.graph.get_edge_data(pred, node_id)
                    if edge_data and edge_data.get("type") == "contradicts":
                        contradictions.append({
                            "step": entry,
                            "contradicts_id": pred
                        })
        
        return {
            "topic": topic,
            "total_nodes_considered": len(similar_nodes),
            "key_concepts": concepts[:10],
            "supporting_evidence": evidence[:10],
            "identified_contradictions": contradictions[:5],
            "synthesis_timestamp": datetime.now().isoformat()
        }
    
    def save(self) -> None:
        """Persist the graph to disk."""
        data = {
            "nodes": [
                {"id": n, **self.graph.nodes[n]}
                for n in self.graph.nodes()
            ],
            "edges": [
                {"source": u, "target": v, **self.graph.edges[u, v]}
                for u, v in self.graph.edges()
            ],
            "saved_at": datetime.now().isoformat()
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self) -> None:
        """Load graph from disk."""
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        
        self.graph = nx.DiGraph()
        
        for node_data in data.get("nodes", []):
            node_id = node_data.pop("id")
            self.graph.add_node(node_id, **node_data)
            if "embedding" in node_data:
                self._embeddings_cache[node_id] = np.array(node_data["embedding"])
        
        for edge_data in data.get("edges", []):
            source = edge_data.pop("source")
            target = edge_data.pop("target")
            self.graph.add_edge(source, target, **edge_data)
    
    def get_stats(self) -> Dict[str, int]:
        """Get graph statistics."""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": {
                node_type: sum(1 for _, d in self.graph.nodes(data=True) 
                              if d.get("type") == node_type)
                for node_type in self.NODE_TYPES
            }
        }
