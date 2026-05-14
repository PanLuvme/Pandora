# Skill: Schema Abstraction

## What this does in the brain
Based on Rumelhart's schema theory. A schema is a
reusable knowledge structure — an abstract pattern
that recurs across different domains. When you notice
that market competition, evolutionary selection, and
immune response all share the same underlying structure
of adversarial selection under resource constraint,
you have abstracted a schema.

Schema abstraction finds groups of nodes from different
domains that share the same action tags — meaning they
all implement the same type of operation. It then
prompts you to name the abstract pattern, which becomes
a schema node that all instances connect to.

## The compounding effect
Once a schema exists, every future node that matches
it inherits the schema's connections automatically.
Instead of manually linking a new note to everything
related, it links to the schema and inherits the
entire conceptual neighborhood for free.

## Example
Nodes about backpropagation, gradient descent, and
reinforcement learning all share Action/Optimize.
Schema abstraction notices this and asks: what is
the abstract optimization pattern they share?
Your answer becomes a schema node that accelerates
learning across all optimization-related captures.

## Tools I expose
- detect() — finds schema candidates in the graph
- match(node_tags) — checks if a new node matches
  an existing schema

## Schedule
Runs every Sunday at 04:30 via daemon.
