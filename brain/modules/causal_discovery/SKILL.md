# Skill: Causal Discovery

## What this does in the brain
Finds causal structure in your knowledge graph. When two
concepts are consistently retrieved together and one is
more fundamental than the other, causal discovery infers
a CAUSES relationship between them.

This transforms the graph from a collection of related
concepts into a directed causal map. You can ask: what
are the root causes of this problem? What does this
concept lead to? Which upstream ideas would resolve
this downstream question?

## How causality is inferred
Uses co-activation patterns from stigmergic memory.
When A and B are co-activated frequently and A has
higher activation count than B, A likely causes B.
The CAUSES edge is created with a strength score.

## Root cause traversal
Given any node, causal discovery can walk backwards
along CAUSES edges to find the fundamental upstream
concepts — the smallest set of ideas that explain
everything downstream.

## Requires
Spreading activation must be running to build
CO_ACTIVATED relationships first. Needs at least
3 co-activations before inferring causality.

## Tools I expose
- discover(min_observations) — finds and creates causal edges
- get_root_causes(node_id) — traces upstream causes

## Schedule
Runs weekly via daemon.
