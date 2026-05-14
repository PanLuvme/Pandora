import json
import os
from config import REGISTRY_PATH


class RegistryReader:
    def __init__(self, path: str = REGISTRY_PATH):
        self.path = path
        self._data = {}
        self.reload()

    def reload(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                self._data = json.load(f)
        else:
            self._data = {"modules": {}}

    def is_enabled(self, module_id: str) -> bool:
        return (self._data
                .get("modules", {})
                .get(module_id, {})
                .get("enabled", False))

    def list_enabled(self) -> list:
        return [
            mid for mid, m in
            self._data.get("modules", {}).items()
            if m.get("enabled", False)
        ]

    def get_schema(self, module_id: str) -> dict:
        schemas = {
            "tiered-memory":        {"tools": ["run_tier_promotion_demotion", "get_tier_weighted_results"]},
            "subconscious":         {"tools": ["run_burst", "run_burst_adaptive", "run_single_loop"]},
            "semantic-dedup":       {"tools": ["check_and_deduplicate"]},
            "entity-resolution":    {"tools": ["find_and_merge_entities"]},
            "neo4j-traversal":      {"tools": ["traverse", "find_gaps", "find_emergence", "sync_node", "run_inference"]},
            "spreading-activation": {"tools": ["activate", "get_co_activations"]},
            "temporal-decay":       {"tools": ["apply", "get_stale_nodes"]},
            "stigmergic-memory":    {"tools": ["deposit", "evaporate", "retrieve"]},
            "surprise-weighting":   {"tools": ["calculate"]},
            "mdl-pruning":          {"tools": ["analyze"]},
            "active-learning":      {"tools": ["rank"]},
            "conceptual-blending":  {"tools": ["find_candidates", "create_blend"]},
            "tda-gap-detection":    {"tools": ["run"]},
            "schema-abstraction":   {"tools": ["detect", "match"]},
            "causal-discovery":     {"tools": ["discover", "get_root_causes"]},
            "self-state":           {"tools": ["generate"]},
            "research-engine":      {"tools": ["search_arxiv", "evaluate_relevance", "write_findings"]},
            "self-improvement":     {"tools": ["evaluate_and_propose"]},
            "connectors":           {"tools": ["fetch_and_ingest"]},
        }
        return schemas.get(module_id, {"error": "unknown module"})
