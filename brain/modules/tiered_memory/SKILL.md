# Skill: Tiered Memory

## What this does in the brain
Pandora's memory works like the human brain — not everything
is equally accessible. Frequently used knowledge stays HOT
and surfaces instantly. Knowledge you have not touched in
weeks cools to WARM, then COOL, then COLD. This prevents
the brain from drowning in old information when you ask a
question. It answers from what actually matters right now.

## The four tiers
- HOT: accessed in the last 24 hours — surfaces first always
- WARM: accessed in the last 7 days — normal weight
- COOL: accessed in the last 30 days — lower weight
- COLD: not accessed in 30+ days — barely surfaces unless
  directly relevant

## When to use me
- After any retrieval session to weight results by recency
- When the brain feels slow or noisy — cold nodes are dragging
  down retrieval quality
- When you want to know what you have been thinking about most

## Tools I expose
- run_tier_promotion_demotion() — runs hourly via daemon
- get_tier_weighted_results(node_ids) — weights any node list by tier

## Schedule
Runs automatically every hour via the daemon.
