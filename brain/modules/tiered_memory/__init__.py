from datetime import datetime, timedelta
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
from utils import log_metrics, write_module_health

class TieredMemory:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)
            )
            self.driver.verify_connectivity()
            self.connected = True
        except Exception as e:
            print(f"TieredMemory Neo4j unavailable: {e}")
            self.connected = False

    def run_tier_promotion_demotion(self, params: dict = {}) -> dict:
        if not self.connected:
            return {"status": "neo4j not connected"}
        now = datetime.now()
        promoted = 0
        demoted = 0
        try:
            with self.driver.session() as session:
                r = session.run("""
                    MATCH (n:Note)
                    WHERE coalesce(n.memory_tier,'warm') = 'hot'
                    AND n.last_activated IS NOT NULL
                    AND datetime(n.last_activated) < datetime($cutoff)
                    SET n.memory_tier = 'warm'
                    RETURN count(n) as count
                """, cutoff=(now - timedelta(hours=24)).isoformat())
                demoted += r.single()["count"] or 0

                r = session.run("""
                    MATCH (n:Note)
                    WHERE coalesce(n.memory_tier,'warm') = 'warm'
                    AND n.last_activated IS NOT NULL
                    AND datetime(n.last_activated) < datetime($cutoff)
                    AND coalesce(n.activation_count,0) < 3
                    SET n.memory_tier = 'cool'
                    RETURN count(n) as count
                """, cutoff=(now - timedelta(days=7)).isoformat())
                demoted += r.single()["count"] or 0

                r = session.run("""
                    MATCH (n:Note)
                    WHERE coalesce(n.memory_tier,'warm') = 'cool'
                    AND n.last_activated IS NOT NULL
                    AND datetime(n.last_activated) < datetime($cutoff)
                    SET n.memory_tier = 'cold'
                    RETURN count(n) as count
                """, cutoff=(now - timedelta(days=30)).isoformat())
                demoted += r.single()["count"] or 0

                r = session.run("""
                    MATCH (n:Note)
                    WHERE coalesce(n.memory_tier,'warm') IN ['cold','cool','warm']
                    AND n.last_activated IS NOT NULL
                    AND datetime(n.last_activated) > datetime($cutoff)
                    SET n.memory_tier = 'hot'
                    RETURN count(n) as count
                """, cutoff=(now - timedelta(hours=1)).isoformat())
                promoted += r.single()["count"] or 0

                dist_result = session.run("""
                    MATCH (n:Note)
                    RETURN coalesce(n.memory_tier,'warm') as tier,
                           count(n) as count
                    ORDER BY tier
                """)
                distribution = {r["tier"]: r["count"] for r in dist_result}

            log_metrics(
                f"tiered_memory | promoted:{promoted} "
                f"demoted:{demoted} dist:{distribution}"
            )
            write_module_health("tiered-memory", {
                "status": "healthy",
                "error_count": 0,
                "metrics": {
                    "promoted": promoted,
                    "demoted": demoted,
                    **{f"tier_{k}": v for k, v in distribution.items()}
                }
            })
            return {
                "promoted": promoted,
                "demoted": demoted,
                "distribution": distribution
            }
        except Exception as e:
            return {"error": str(e)}

    def get_tier_weighted_results(self, params: dict = {}) -> dict:
        if not self.connected:
            return {"nodes": []}
        node_ids = params.get("node_ids", [])
        tier_weights = {"hot": 2.0, "warm": 1.5, "cool": 1.0, "cold": 0.3}
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Note)
                    WHERE size($ids) = 0 OR n.id IN $ids
                    RETURN n.id as id,
                           n.aliases as aliases,
                           coalesce(n.memory_tier,'warm') as tier,
                           coalesce(n.weight,1.0) as weight
                    LIMIT 15
                """, ids=node_ids)
                nodes = []
                for r in result:
                    tier = r["tier"] or "warm"
                    tw = tier_weights.get(tier, 1.0)
                    nodes.append({
                        "id": r["id"],
                        "aliases": r["aliases"],
                        "tier": tier,
                        "score": float(r["weight"] or 1.0) * tw
                    })
                nodes.sort(key=lambda x: x["score"], reverse=True)
            return {"nodes": nodes}
        except Exception as e:
            return {"error": str(e), "nodes": []}
