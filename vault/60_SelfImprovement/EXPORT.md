# Pandora Self Export
Generated: 2026-05-14T19:56:45.232402

## Identity
{
  "name": "Pandora",
  "type": "Living second brain \u2014 mycelium architecture",
  "vault": "/Users/pan/Pandora/vault",
  "github": "https://github.com/PanLuvme/Pandora",
  "description": "Local-first cognitive infrastructure. Captures, stores, retrieves, and grows knowledge using graph intelligence, biological algorithms, and a self-improvement loop that searches arxiv every 14 days."
}

## Graph
- Nodes: 7
- Orphans: 2
- Avg connections: 2.0
- Memory tiers: {'hot': 2, 'warm': 5}
- Edge types: [{'type': 'RELATED', 'count': 6}, {'type': 'IMPLEMENTS', 'count': 1}]

## All Nodes

### 20260514000004 — ['Obsidian']
Tier: warm | Weight: 1.0 | Captured: 2026-05-14
Tags: ['Domain/Software', 'Action/Implement']
Edges: {'related': [20260513212200, 20260514000001]}
Content: # Obsidian

Obsidian is a markdown-based note-taking application that uses **wikilinks** (`[[Note Title]]`) to create a personal knowledge graph stored entirely as plain text files on disk.

## Core Model

- **Notes** are individual `.md` files — no proprietary format, no database lock-in
- **Wikili

### 20260514143000 — ['Stigmergy', 'Indirect Coordination', 'Pheromone Trails']
Tier: hot | Weight: 2.0 | Captured: 2026-05-14
Tags: ['Domain/CognitiveArchitecture', 'Domain/ComplexSystems', 'Action/Retrieve']
Edges: [{'implements': 20260514999999}, {'inspired_by': 'Pierre-Paul Grassé 1959 (termite behavior)'}, {'instantiates': 'stigmergic-memory module'}]
Content: ## Core Idea

Stigmergy is a mechanism of **indirect coordination** where agents leave traces in
the environment that influence the behavior of other agents — without direct
communication between them.

## Origin

Coined by **Pierre-Paul Grassé in 1959** while studying termite colony behavior.
Termi

### 20260514000001 — ['Neo4j']
Tier: warm | Weight: 1.0 | Captured: 2026-05-14
Tags: ['Domain/Software', 'Action/Implement']
Edges: {'implements': [20260513212200]}
Content: # Neo4j

Neo4j is a native graph database management system that stores data as nodes, relationships, and properties rather than in tables or documents. It is optimized for traversing highly connected data efficiently.

## Core Concepts

**Nodes** represent entities (e.g., Person, Product). **Relati

### 20260514000002 — ['AI Agent-Driven KG Construction']
Tier: warm | Weight: 1.0 | Captured: 2026-05-14
Tags: ['Domain/Research', 'Domain/Software', 'Action/Implement']
Edges: {'related': [20260514000001, 20260514000003]}
Content: # AI Agent-Driven Framework for Automated Product Knowledge Graph Construction

A fully automated pipeline that uses AI agents to construct product-specific **Knowledge Graphs (KGs)** directly from unstructured e-commerce data — eliminating the traditionally manual, complex KG construction process.

### 20260514000003 — ['Multi-Agent Semantic Mapping to KG']
Tier: warm | Weight: 1.0 | Captured: 2026-05-14
Tags: ['Domain/Research', 'Domain/Software', 'Action/Implement']
Edges: {'related': [20260514000001, 20260514000002]}
Content: # Multi-Agent System for Semantic Mapping of Relational Data to Knowledge Graphs

A novel approach for integrating multiple siloed relational databases by using **LLMs as semantic agents** to map and co-align their schemas into a unified Knowledge Graph.

## Problem

Enterprises store critical data

### 20260513212200 — ['Pandora', 'Pandora Brain']
Tier: hot | Weight: 1.0 | Captured: 2026-05-13
Tags: ['Domain/Architecture', 'Domain/AI', 'Action/Understand']
Edges: {'implements': [], 'extends': [], 'inspired_by': []}
Content: ## Core idea
Pandora is a living second brain built on a mycelium architecture using Neo4j for graph traversal, LangGraph for multi-agent orchestration, and a Python daemon for 24/7 background processing.

## Detail
The brain grows exponentially through stigmergic memory, spreading activation, and a

## Enabled Modules (17)
- **Tiered Memory** (tiered-memory) | hourly | healthy
  Pandora's memory works like the human brain — not everything is equally accessible. Frequently used knowledge stays HOT and surfaces instantly. Knowle
- **Pandora Subconscious** (subconscious) | every_5_minutes | healthy
  While you are not actively using Pandora, the subconscious runs in the background like a dreaming mind. It picks random nodes and walks their connecti
- **Semantic Deduplication** (semantic-dedup) | on_capture | healthy
  Before any new note enters the vault, this module checks whether you already have something that says the same thing. It embeds the new content as a v
- **Entity Resolution** (entity-resolution) | daily_03:00 | healthy
  When you capture information from multiple sources — a PDF, a Telegram message, a web article — the same concept can appear across all three as separa
- **Neo4j Traversal** (neo4j-traversal) | on_query | healthy
  
- **Spreading Activation** (spreading-activation) | sunday_03:00 | disabled
  Based on cognitive science models of how human memory works. When you think of one concept, related concepts become partially activated in your mind —
- **Temporal Decay** (temporal-decay) | daily_02:00 | disabled
  Knowledge expires at different rates. A note about a Python library from 2022 is probably outdated. A note about Euclidean geometry from 2022 is still
- **Stigmergic Memory** (stigmergic-memory) | daily_02:30 | disabled
  Inspired by ant colonies. When ants find food they leave pheromone trails. Other ants follow the strongest trails. Unused trails evaporate. The colony
- **Surprise Weighting** (surprise-weighting) | on_capture | disabled
  When you capture something new, not all information is equally valuable. Information that genuinely surprises the brain — that says something your exi
- **MDL Pruning** (mdl-pruning) | monthly | disabled
  Minimum Description Length pruning identifies nodes that are informationally redundant — nodes that say nothing the graph does not already know from t
- **Active Learning** (active-learning) | sunday_04:00 | disabled
  Not all questions are equally worth answering. Some questions, if answered, would significantly improve the brain's connectivity and retrieval quality
- **Schema Abstraction** (schema-abstraction) | sunday_04:30 | disabled
  Based on Rumelhart's schema theory. A schema is a reusable knowledge structure — an abstract pattern that recurs across different domains. When you no
- **Causal Discovery** (causal-discovery) | weekly | disabled
  Finds causal structure in your knowledge graph. When two concepts are consistently retrieved together and one is more fundamental than the other, caus
- **Self State Generator** (self-state) | biweekly | healthy
  Pandora reads itself. This module scans the entire brain — every module, every node, every edge — and produces a precise description of its current st
- **Research Engine** (research-engine) | biweekly | healthy
  Pandora reads its own self-state, identifies gaps in its knowledge and capabilities, then searches arxiv for papers that could fill those gaps. It sco
- **Self Improvement Evaluator** (self-improvement) | biweekly | healthy
  Pandora reads its own gaps from the self-state, reads the arxiv papers found by the research engine, and uses the local LLM to generate specific propo
- **Self Export** (self-export) | manual | healthy
  One tool call returns everything about Pandora: every module, every node, graph stats, schedule, gaps, and full diagnostics. Written to EXPORT.md in t

## Disabled Modules
['conceptual-blending', 'tda-gap-detection', 'connectors']

## Schedule
{
  "every_5min": "subconscious.run_burst_adaptive",
  "every_10min": "auto_git_push",
  "every_hour": "tiered_memory.run_tier_promotion_demotion",
  "daily_02:00": "temporal_decay.apply",
  "daily_02:30": "stigmergic_memory.evaporate",
  "daily_03:00": "entity_resolution.find_and_merge_entities",
  "sunday": "tda, active_learning, schema, mdl_pruning",
  "weekly": "causal_discovery.discover",
  "every_14days": "self_state \u2192 research_engine \u2192 self_improvement"
}

## Gaps
{
  "not_built": [
    "TDA gap detection",
    "Brain Manager Obsidian plugin",
    "LangGraph orchestrator in MCP",
    "Mobile capture"
  ],
  "nodes_until_full_activation": 43
}
