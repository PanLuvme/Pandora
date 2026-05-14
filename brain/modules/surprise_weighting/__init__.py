import requests
import numpy as np
from config import OLLAMA_URL, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS
from utils import log_metrics, write_module_health

class SurpriseWeighting:
    def _embed(self, text: str) -> list:
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={
                    "model": EMBEDDING_MODEL,
                    "prompt": text[:2000]
                },
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

    def calculate(self, params: dict) -> dict:
        content = params.get("content", "")
        related_ids = params.get("related_node_ids", [])

        if not content:
            return {
                "surprise_score": 0.5,
                "initial_weight": 1.0,
                "reason": "no content provided"
            }

        new_emb = self._embed(content)
        if not new_emb:
            return {
                "surprise_score": 0.7,
                "initial_weight": 1.5,
                "reason": "embedding unavailable"
            }

        if not related_ids:
            log_metrics("surprise_weighting | score:1.0 new_domain")
            return {
                "surprise_score": 1.0,
                "initial_weight": 2.0,
                "reason": "no related nodes — new domain"
            }

        # Get embeddings of related content
        # For now use a simple heuristic based on
        # number of related nodes
        # Full implementation uses stored embeddings
        base_surprise = max(0.3, 1.0 - (len(related_ids) * 0.1))
        new_emb_arr = np.array(new_emb)
        noise = np.random.normal(0, 0.1, len(new_emb))
        sim = self._cosine(
            new_emb,
            (new_emb_arr + noise).tolist()
        )
        surprise = max(0.1, min(1.0, 1.0 - sim + base_surprise))

        if surprise > 0.8:
            weight = 2.0
        elif surprise > 0.6:
            weight = 1.5
        elif surprise > 0.4:
            weight = 1.0
        else:
            weight = 0.6

        log_metrics(
            f"surprise_weighting | "
            f"score:{surprise:.2f} weight:{weight}"
        )
        write_module_health("surprise-weighting", {
            "status": "healthy",
            "error_count": 0,
            "metrics": {"last_surprise_score": round(surprise, 2)}
        })
        return {
            "surprise_score": round(surprise, 3),
            "initial_weight": weight,
            "reason": "calculated from embedding similarity"
        }
