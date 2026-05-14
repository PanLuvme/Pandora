# Skill: Entity Resolution

## What this does in the brain
When you capture information from multiple sources —
a PDF, a Telegram message, a web article — the same
concept can appear across all three as separate nodes.
Entity resolution finds these duplicates across sources
and links them with a SAME_ENTITY edge, collapsing
fragmented knowledge into unified understanding.

## Example
You capture a note about "LangGraph" from a YouTube video.
Later you capture a PDF that also mentions "LangGraph".
Without entity resolution: two disconnected nodes.
With entity resolution: one unified concept with edges
to both sources.

## How it works
Compares aliases across nodes from different sources.
When two nodes share an alias but come from different
sources, it creates a SAME_ENTITY relationship between
them. The graph stays connected across all input channels.

## Tools I expose
- find_and_merge_entities() — runs daily via daemon

## Schedule
Runs automatically every day at 03:00 via daemon.
