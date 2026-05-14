# Skill: MDL Pruning

## What this does in the brain
Minimum Description Length pruning identifies nodes that
are informationally redundant — nodes that say nothing
the graph does not already know from their neighbors.

A node is redundant if everything it contains can be
predicted from its connected nodes. High redundancy
means the node adds noise, not signal. MDL pruning
flags these for human review — never deletes them
automatically.

## The math
Redundancy score = (neighbor_count / neighbor_count+1)
                   × (1 / log2(2 + activation))

High neighbors + low activation = likely redundant.
The activation penalty ensures frequently-used nodes
are never flagged even if they have many connections.

## Threshold
Default: 0.92 — only extremely redundant nodes flagged.
Nodes below threshold are safe and informationally unique.

## Tools I expose
- analyze(threshold) — runs monthly via daemon

## Schedule
Runs automatically once a month.
Never deletes. Only flags for human review.
