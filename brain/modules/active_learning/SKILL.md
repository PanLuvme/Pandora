# Skill: Active Learning

## What this does in the brain
Not all questions are equally worth answering. Some
questions, if answered, would significantly improve
the brain's connectivity and retrieval quality. Others
would add one isolated note that connects to nothing.

Active learning ranks your open questions by epistemic
value — how much answering each question would improve
the entire graph. Questions that touch many existing
nodes and underexplored areas rank highest. These are
the highest-priority capture targets.

## Epistemic value calculation
- Reachable nodes from source: how connected is the
  area around this question? More reachable = higher value
- Activation count inverse: questions from rarely-accessed
  nodes score higher — they need attention more
- Combined score: (reachable × 0.4) + (5 - activation × 0.6)

## The result
Instead of answering questions randomly, Pandora tells
you which questions matter most to its own growth.
You answer those first. The brain grows directionally
toward its own most important gaps.

## Tools I expose
- rank(top_n) — ranks all open questions by epistemic value

## Schedule
Runs every Sunday at 04:00 via daemon.
Also run manually before a capture session to know
what to focus on.
