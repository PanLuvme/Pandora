# Skill: Semantic Deduplication

## What this does in the brain
Before any new note enters the vault, this module checks
whether you already have something that says the same thing.
It embeds the new content as a vector and compares it
against all existing nodes using cosine similarity. If the
similarity is above 92% the content is a duplicate — merge
it. Between 80-92% it is similar — extend an existing node.
Below 80% it is genuinely new — proceed with capture.

## Why this matters
Without deduplication, the graph accumulates noise. Three
articles about the same topic become three disconnected
nodes that dilute retrieval and confuse the subconscious.
Deduplication keeps the graph dense and signal-rich.

## Verdicts
- duplicate (>92%): do not create a new node, merge content
- similar (80-92%): consider extending existing node
- unique (<80%): safe to capture as new node

## Requirements
Needs Ollama running locally for embeddings.
Uses mxbai-embed-large model, truncated to 512 dimensions.

## Tools I expose
- check_and_deduplicate(content, threshold_dup, threshold_sim)

## When it runs
Called automatically during every capture pipeline execution.
