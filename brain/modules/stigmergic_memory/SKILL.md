# Skill: Stigmergic Memory

## What this does in the brain
Inspired by ant colonies. When ants find food they leave
pheromone trails. Other ants follow the strongest trails.
Unused trails evaporate. The colony self-organizes around
what actually works without any central control.

Pandora does the same with knowledge. When a retrieval
path successfully answers a question, pheromone is
deposited on every node and edge in that path. Future
retrievals are biased toward high-pheromone paths.
Paths that never help evaporate over time.

## The result
The brain develops dominant hyphae — well-worn paths
through your knowledge that reliably produce good answers.
Your most useful intellectual connections grow stronger
automatically. Dead ends fade away.

## How pheromone works
- Successful retrieval: +1.0 pheromone on path
- Failed retrieval: -0.1 pheromone on path
- Daily evaporation: all pheromone × 0.95
- Retrieval scoring: weight × 0.6 + pheromone × 0.4

## Tools I expose
- deposit(path_node_ids, query_success)
- evaporate() — runs daily via daemon
- retrieve(seed_ids) — pheromone-weighted retrieval

## Schedule
Evaporation runs automatically every day at 02:30.
Deposit is called after every successful retrieval.
