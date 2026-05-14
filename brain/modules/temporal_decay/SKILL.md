# Skill: Temporal Decay

## What this does in the brain
Knowledge expires at different rates. A note about a
Python library from 2022 is probably outdated. A note
about Euclidean geometry from 2022 is still perfectly
valid. Temporal decay makes Pandora honest about this.

Every node gets a temporal_weight between 0.1 and 1.0
calculated from its age and domain. Recent notes in
fast-moving domains score close to 1.0. Old notes in
stable domains also stay close to 1.0. Old notes in
fast-moving domains decay toward 0.1 — still retrievable
but flagged as potentially stale.

## Domain half-lives
- Finance: 90 days
- Technology / AI: 180 days
- Business / Software: 1 year
- Medicine / Psychology: 2 years
- Science: 5 years
- Mathematics / Philosophy / History: 100 years

## How it affects retrieval
Retrieval scoring uses temporal_weight × activation_weight.
A stale note about a deprecated library will not surface
above a fresh note about its replacement.

## Tools I expose
- apply() — runs daily, updates all temporal weights
- get_stale_nodes(threshold) — lists nodes below threshold

## Schedule
Runs automatically every day at 02:00 via daemon.
