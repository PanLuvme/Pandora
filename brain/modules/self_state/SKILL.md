# Skill: Self State Generator

## What this does in the brain
Pandora reads itself. This module scans the entire brain —
every module, every node, every edge — and produces a
precise description of its current state. It identifies
where the brain is weak, what domains are sparse, which
modules are disabled, and what questions the brain should
be researching next to grow.

## Why this matters
A brain that cannot describe itself cannot improve itself.
The self state is the input to the research engine. Without
it, the arxiv search is generic. With it, the search is
targeted at exactly what this brain is missing.

## What it produces
- /60_SelfImprovement/SELF_STATE.md updated with current stats
- List of identified gaps with specific descriptions
- Search queries generated from those gaps for arxiv research

## Tools I expose
- generate() — produces full brain self-description

## Schedule
Runs every 14 days automatically via daemon.
Also runs manually before any research engine cycle.
