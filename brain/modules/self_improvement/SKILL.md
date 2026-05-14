# Skill: Self Improvement Evaluator

## What this does in the brain
Pandora reads its own gaps from the self-state, reads the
arxiv papers found by the research engine, and uses the
local LLM to generate specific proposals for new modules
it could add to itself to become smarter.

## The output
Three ranked proposals written to IMPROVEMENT_QUEUE.md.
Each proposal includes the module ID, what gap it solves,
which paper it implements, and complexity rating. You
review each one and approve or reject it. Approved
proposals get implemented as real Python modules.

## Why human approval matters
The brain proposes. You decide. The self improvement
evaluator never implements anything automatically. It
surfaces options based on research and lets you choose
the direction Pandora grows. This prevents the brain
from optimizing toward things you do not actually want.

## Requirements
Needs Ollama running locally for proposal generation.
Needs self-state and arxiv findings to exist first.

## Tools I expose
- evaluate_and_propose() — reads state, generates proposals

## Schedule
Runs every 14 days as part of the self-improvement cycle.
