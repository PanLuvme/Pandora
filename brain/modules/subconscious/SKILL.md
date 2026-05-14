# Skill: Pandora Subconscious

## What this does in the brain
While you are not actively using Pandora, the subconscious
runs in the background like a dreaming mind. It picks random
nodes and walks their connections, looking for two concepts
that share neighbors but have never been directly linked.
When it finds one, it writes a subconscious insight. These
are the unexpected connections — the ones you would never
think to search for but that turn out to be the most
generative ideas in your knowledge graph.

## Inspiration
Based on the Purkinje cell — the neuron responsible for
random thought generation in the human cerebellum. Most AI
systems only model the conscious mind. Pandora models both.

## How it runs
Every 5 minutes the daemon triggers a burst of loops.
Each loop: pick a random node → walk its edges → check if
any two nodes in the neighborhood share common neighbors
but no direct link. If yes — emergence detected, insight
written to /60_SelfImprovement/SUBCONSCIOUS_INSIGHTS.md

## CPU awareness
Uses psutil to check CPU load before running. Pauses when
you are actively working (CPU > 70%). Runs full bursts when
your machine is idle. Never slows you down.

## Tools I expose
- run_single_loop() — one subconscious cycle
- run_burst(loops) — N loops in rapid succession
- run_burst_adaptive() — CPU-aware burst, runs via daemon

## Schedule
Every 5 minutes automatically via daemon.
