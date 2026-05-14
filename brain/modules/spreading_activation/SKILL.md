# Skill: Spreading Activation

## What this does in the brain
Based on cognitive science models of how human memory
works. When you think of one concept, related concepts
become partially activated in your mind — not fully
recalled but primed and ready. This is spreading
activation.

Pandora does the same. When you query for a topic,
activation spreads outward from the matching nodes
along edges, with the signal decaying at each hop.
Nodes that fire above the threshold get included in
the response even if you did not search for them
directly. This surfaces connections you did not know
to look for.

## Decay mechanics
- Seed nodes: activation = 1.0
- Each hop: activation × 0.7 (configurable)
- Threshold: 0.15 — nodes below this do not fire
- Max hops: 4 — signal cannot travel more than 4 edges

## Example
You search for "Neo4j". Spreading activation fires:
- Neo4j (1.0) → graph databases (0.7) →
  knowledge graphs (0.49) → LLM reasoning (0.34) →
  Pandora architecture (0.24)
You get the full conceptual neighborhood, not just
the exact match.

## Tools I expose
- activate(seed_ids, decay, threshold, max_hops)
- get_co_activations(min_co_count)

## When it runs
Called during retrieval after initial seed search.
Extends the result set with conceptually related nodes.
