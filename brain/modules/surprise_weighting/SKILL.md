# Skill: Surprise Weighting

## What this does in the brain
When you capture something new, not all information is
equally valuable. Information that genuinely surprises
the brain — that says something your existing nodes do
not already cover — deserves more weight than information
that confirms what you already know.

Surprise weighting embeds the new content and compares
it against existing knowledge. High surprise means the
content is genuinely new to the brain. Low surprise means
it mostly confirms existing nodes. The initial node weight
is set accordingly.

## Surprise to weight mapping
- Surprise > 0.8: weight 2.0 — highly novel, surfaces first
- Surprise > 0.6: weight 1.5 — moderately novel
- Surprise > 0.4: weight 1.0 — normal
- Surprise < 0.4: weight 0.6 — mostly confirmatory

## Why this matters
Without surprise weighting every note starts equal.
With it the brain automatically prioritizes genuinely
new knowledge over redundant confirmations. This is
how the brain stays signal-rich as it scales.

## Tools I expose
- calculate(content, related_node_ids)

## When it runs
Called during every capture pipeline before writing.
