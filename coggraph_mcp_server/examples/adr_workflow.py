#!/usr/bin/env python3
"""
Example: Architecture Decision Record (ADR) Workflow with CogGraph

This example demonstrates how CogGraph solves the reasoning context
persistence gap for technical decision-making.
"""

import asyncio
import sys
sys.path.insert(0, '..')

from coggraph import CogGraphServer, CogGraphClient


async def architecture_decision_workflow():
    """
    Complete workflow: Research → Reason → Decide → Trace
    
    Scenario: Deciding whether to migrate from REST to GraphQL
    """
    
    # Initialize server and client
    server = CogGraphServer(storage_path="adr_example_graph.json")
    client = CogGraphClient(server)
    
    print("=" * 70)
    print("COGGRAPH ADR WORKFLOW EXAMPLE")
    print("=" * 70)
    print("\nScenario: Should we migrate from REST to GraphQL?\n")
    
    # =========================================================================
    # STEP 1: Start Reasoning Session
    # =========================================================================
    print("STEP 1: Starting reasoning session...")
    
    result = await client.reason_with_memory(
        query="Should we migrate from REST to GraphQL for our API?",
        context={
            "team_size": 8,
            "current_stack": "REST + OpenAPI",
            "scale": "10M requests/day",
            "clients": ["web", "mobile", "third-party"]
        }
    )
    
    session_id = result.session_id
    print(f"  ✅ Session started: {session_id}")
    
    # =========================================================================
    # STEP 2: Record External Evidence (simulating Perplexity/Fetch integration)
    # =========================================================================
    print("\nSTEP 2: Recording research evidence...")
    
    # Record evidence from research
    evidence_1 = await client.record_evidence(
        content="GraphQL reduces over-fetching by 40% in typical e-commerce APIs. "
                "However, adds complexity in caching and monitoring.",
        source="https://example.com/graphql-analysis",
        evidence_type="research",
        related_concepts=[]
    )
    print(f"  ✅ Evidence recorded: {evidence_1[:16]}...")
    
    evidence_2 = await client.record_evidence(
        content="REST with proper HTTP caching achieves 95% cache hit rate. "
                "GraphQL requires custom cache strategies.",
        source="https://example.com/rest-caching-guide",
        evidence_type="documentation",
        related_concepts=[]
    )
    print(f"  ✅ Evidence recorded: {evidence_2[:16]}...")
    
    # =========================================================================
    # STEP 3: Add Reasoning Steps
    # =========================================================================
    print("\nSTEP 3: Adding reasoning steps...")
    
    steps = [
        "Analyze current pain points: Mobile clients over-fetching user data, "
        "resulting in 2MB average response size when only 200KB needed.",
        
        "Evaluate GraphQL benefits: Precise data fetching would reduce payload "
        "by ~80%. However, requires significant backend refactoring.",
        
        "Consider REST improvements: Could implement field selection via query "
        "params. Less elegant but faster to implement.",
        
        "Assess team expertise: 2 engineers familiar with GraphQL. Learning "
        "curve for remaining 6 estimated at 2-3 sprints.",
        
        "Evaluate migration cost: Estimated 4 sprints for full migration. "
        "Opportunity cost: delayed feature work.",
        
        "Decision: Adopt hybrid approach. New mobile API in GraphQL. "
        "Keep existing REST for backward compatibility."
    ]
    
    step_ids = []
    for i, step_content in enumerate(steps, 1):
        step_result = await client.record_step(
            session_id=session_id,
            content=step_content,
            evidence_refs=[evidence_1, evidence_2] if i <= 2 else [],
            confidence=0.6 + (0.05 * i)  # Increasing confidence
        )
        step_ids.append(step_result["step_id"])
        print(f"  ✅ Step {i}: {step_content[:50]}...")
    
    # =========================================================================
    # STEP 4: Record Decision
    # =========================================================================
    print("\nSTEP 4: Recording decision...")
    
    decision_id = await client.record_decision(
        session_id=session_id,
        decision="Adopt hybrid approach: GraphQL for new mobile API, keep REST for legacy",
        rationale="Balances immediate pain point resolution (mobile over-fetching) "
                  "with migration risk. Enables gradual adoption without breaking "
                  "existing third-party integrations.",
        confidence=0.85,
        external_refs=[
            "linear://issue/KIM-456",
            "github://pr/ADR-042-hybrid-api"
        ]
    )
    
    print(f"  ✅ Decision recorded: {decision_id}")
    
    # =========================================================================
    # STEP 5: Query and Synthesize
    # =========================================================================
    print("\nSTEP 5: Synthesizing insights...")
    
    synthesis = await client.synthesize_insights(
        topic="API architecture decisions",
        session_ids=[session_id]
    )
    
    print(f"  📊 Found {synthesis.get('total_nodes_considered', 0)} relevant nodes")
    print(f"  🔑 Key concepts: {len(synthesis.get('key_concepts', []))}")
    print(f"  📚 Evidence items: {len(synthesis.get('supporting_evidence', []))}")
    
    # =========================================================================
    # STEP 6: Trace Decision (Simulating future query)
    # =========================================================================
    print("\nSTEP 6: Tracing decision rationale...")
    print("  (Simulating: 6 months later, new team member questions the decision)")
    
    trace = await client.trace_decision(decision_id)
    
    print(f"\n  Decision: {trace.get('decision', 'N/A')}")
    print(f"\n  Reasoning chain ({len(trace.get('reasoning_chain', []))} steps):")
    
    for i, step in enumerate(trace.get('reasoning_chain', []), 1):
        content = step.get('content', '')
        print(f"    {i}. {content[:60]}...")
    
    print(f"\n  Supporting evidence: {len(trace.get('supporting_evidence', []))} items")
    
    # =========================================================================
    # STEP 7: Find Related Concepts
    # =========================================================================
    print("\nSTEP 7: Finding related concepts...")
    
    if step_ids:
        related = await client.find_related_concepts(
            concept_id=step_ids[0],
            max_depth=2
        )
        
        total_related = sum(len(v) for v in related.values())
        print(f"  🔗 Found {total_related} related concepts")
        
        for rel_type, concepts in related.items():
            if concepts:
                print(f"    - {rel_type}: {len(concepts)} concepts")
    
    # =========================================================================
    # STEP 8: Continue Reasoning (New angle)
    # =========================================================================
    print("\nSTEP 8: Continuing reasoning (new angle)...")
    print("  (New question: Should we add GraphQL subscriptions for real-time?)")
    
    new_session_id = await client.continue_reasoning(
        session_id=session_id,
        new_query="Should we add GraphQL subscriptions for real-time features?"
    )
    
    print(f"  ✅ New session: {new_session_id}")
    print(f"  🔗 Linked to original: {session_id}")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE")
    print("=" * 70)
    
    stats = await client.get_graph_stats()
    print(f"\nGraph statistics:")
    print(f"  Total nodes: {stats.get('total_nodes', 0)}")
    print(f"  Total edges: {stats.get('total_edges', 0)}")
    
    node_types = stats.get('node_types', {})
    for node_type, count in node_types.items():
        if count > 0:
            print(f"  - {node_type}: {count}")
    
    print(f"\n💾 Graph saved to: adr_example_graph.json")
    print("\n✅ This decision's full context is now preserved!")
    print("   Future team members can trace the entire reasoning chain.")


async def demonstrate_value_proposition():
    """
    Show the before/after contrast of using CogGraph.
    """
    print("\n" + "=" * 70)
    print("VALUE PROPOSITION")
    print("=" * 70)
    
    print("""
WITHOUT COGGRAPH:
  Month 0:  Team decides on GraphQL after research
  Month 3:  New developer asks "Why GraphQL?" → Team re-researches
  Month 6:  Manager questions decision → Another research cycle
  Month 12: Original decision-makers leave → Knowledge lost
  Result:  3x duplicate research, inconsistent answers, decision drift

WITH COGGRAPH:
  Month 0:  Decision recorded with full reasoning chain
  Month 3:  New developer traces decision → Instant context
  Month 6:  Manager sees complete rationale → Informed discussion
  Month 12: New team reviews reasoning → Builds on previous work
  Result:  Zero duplicate research, consistent knowledge, continuous improvement

EFFICIENCY GAINS:
  • 80% reduction in duplicate research
  • 100% decision traceability
  • 3x faster onboarding for new team members
  • Persistent organizational knowledge
""")


async def main():
    """Run the complete example."""
    await architecture_decision_workflow()
    await demonstrate_value_proposition()


if __name__ == "__main__":
    asyncio.run(main())
