# Skill: Research Engine

## What this does in the brain
Pandora reads its own self-state, identifies gaps in its
knowledge and capabilities, then searches arxiv for papers
that could fill those gaps. It scores each paper on
recency, gap alignment, implementability, and PKM
relevance. The top results are written to your vault as
an improvement queue you review and decide on.

## The self-improvement loop
1. Self state generator identifies brain gaps
2. Research engine converts gaps into arxiv queries
3. Papers are scored and ranked
4. Top papers written to /60_SelfImprovement/
5. You review and approve which to implement
6. New modules get added to the brain

## Why this matters
Most second brain systems are static. They never get
smarter on their own. Pandora identifies what it is
missing and finds the research to fix it. Every 14 days
it looks at what it knows, what it does not know, and
what the latest research says about closing that gap.

## Tools I expose
- search_arxiv(queries, max_per_query)
- evaluate_relevance(papers, gaps)
- write_findings(ranked_papers)

## Schedule
Runs every 14 days as part of the self-improvement cycle.
