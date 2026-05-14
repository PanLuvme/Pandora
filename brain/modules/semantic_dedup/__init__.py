import requests
import numpy as np
from neo4j import GraphDatabase
from config import (
    NEO4J_URI, NEO4J_USER, NEO4J_PASS,
    OLLAMA_URL, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS
)
from utils import log_metrics, write_module_health

class SemanticDedup:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)
            )
            self.driver.verify_connectivity()
            self.connected = True
        except Exception as e:
            print(f"SemanticDedup Neo4j unavailable: {e}")
            self.connected = False

    def _embed(self, text: str) -> list:
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": EMBEDDING_MODEL,
                      "prompt": text[:2000]},
                timeout=30
            )
            emb = r.json().get("embedding", [])
            return emb[:EMBEDDING_DIMENSIONS]
        except Exception:
            return []

    def _cosine(self, a: list, b: list) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        a_arr = np.array(a, dtype=float)
        b_arr = np.array(b, dtype=float)
        n = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
        return float(np.dot(a_arr, b_arr) / n) if n > 0 else 0.0

    def check_and_deduplicate(self, params: dict = {}) -> dict:
        content = params.get("content", "")
        threshold_dup = params.get("threshold_dup", 0.92)
        threshold_sim = params.get("threshold_sim", 0.80)

        if not content:
            return {"verdict": "unique", "reason": "no content"}

        new_emb = self._embed(content)
        if not new_emb:
            return {
                "verdict": "unique",
                "reason": "embedding unavailable — Ollama may be offline"
            }

        if not self.connected:
            return {"verdict": "unique", "reason": "neo4j not connected"}

        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Note)
                    WHERE n.status = 'active'
                    AND n.embedding IS NOT NULL
                    RETURN n.id as id, n.aliases as aliases,
                           n.embedding as embedding
                    ORDER BY n.activation_count DESC
                    LIMIT 200
                """)
                existing = [dict(r) for r in result]
        except Exception as e:
            return {"verdict": "unique", "reason": f"query error: {e}"}

        best_score = 0.0
        best_match = None
        for node in existing:
            emb = node.get("embedding")
            if not emb:
                continue
            score = self._cosine(new_emb, emb)
            if score > best_score:
                best_score = score
                best_match = node

        log_metrics(
            f"semantic_dedup | score:{best_score:.3f} "
            f"match:{best_match['id'] if best_match else 'none'}"
        )
        write_module_health("semantic-dedup", {
            "status": "healthy",
            "error_count": 0,
            "metrics": {"last_score": round(best_score, 3)}
        })

        if best_score >= threshold_dup:
            return {
                "verdict": "duplicate",
                "similarity": best_score,
                "match_id": best_match["id"],
                "match_name": best_match["aliases"],
                "action": "merge into existing node"
            }
        elif best_score >= threshold_sim:
            return {
                "verdict": "similar",
                "similarity": best_score,
                "match_id": best_match["id"],
                "match_name": best_match["aliases"],
                "action": "extend existing node or create with edge"
            }
        else:
            return {
                "verdict": "unique",
                "similarity": best_score,
                "action": "proceed with capture"
            }
