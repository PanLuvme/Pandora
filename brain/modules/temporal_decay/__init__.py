import math
from datetime import datetime
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
from utils import log_metrics, append_to_alerts, write_module_health

DOMAIN_HALF_LIVES = {
    "Domain/Technology":   180,
    "Domain/Software":     365,
    "Domain/Science":      1825,
    "Domain/Mathematics":  36500,
    "Domain/Philosophy":   36500,
    "Domain/History":      36500,
    "Domain/Business":     365,
    "Domain/Finance":      90,
    "Domain/Medicine":     730,
    "Domain/Psychology":   1825,
    "Domain/Physics":      18250,
    "Domain/AI":           180,
    "DEFAULT":             730
}

class TemporalDecay:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS),
                connection_timeout=10
            )
            self.driver.verify_connectivity()
            self.connected = True
        except Exception as e:
            print(f"TemporalDecay Neo4j unavailable: {e}")
            self.connected = False

    def _calculate(self, captured_date: str,
                   tags: list) -> float:
        try:
            captured = datetime.strptime(
                str(captured_date)[:10], "%Y-%m-%d"
            )
            days_old = (datetime.now() - captured).days
        except Exception:
            return 1.0
        half_life = DOMAIN_HALF_LIVES["DEFAULT"]
        for tag in (tags or []):
            if tag in DOMAIN_HALF_LIVES:
                half_life = DOMAIN_HALF_LIVES[tag]
                break
        lambda_val = math.log(2) / half_life
        return max(0.1, math.exp(-lambda_val * days_old))

    def apply(self, params: dict = {}) -> dict:
        if not self.connected:
            return {"status": "skipped"}
        stale = []
        updated = 0
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Note)
                    RETURN n.id as id,
                           n.captured as captured,
                           n.tags as tags
                """)
                nodes = [dict(r) for r in result]

            for node in nodes:
                tw = self._calculate(
                    node.get("captured", ""),
                    node.get("tags", [])
                )
                with self.driver.session() as session:
                    session.run("""
                        MATCH (n:Note {id: $id})
                        SET n.temporal_weight = $tw
                    """, id=node["id"], tw=tw)
                updated += 1
                if tw < 0.3:
                    stale.append({
                        "id": node["id"],
                        "temporal_weight": round(tw, 3)
                    })

            if stale:
                alert = (
                    f"\n## Stale knowledge "
                    f"({len(stale)} nodes below 30%)\n"
                )
                for n in stale[:10]:
                    alert += (
                        f"- [ ] {n['id']} — "
                        f"{n['temporal_weight']:.0%} validity\n"
                    )
                append_to_alerts(alert)

            log_metrics(
                f"temporal_decay | "
                f"updated:{updated} stale:{len(stale)}"
            )
            write_module_health("temporal-decay", {
                "status": "healthy",
                "error_count": 0,
                "metrics": {
                    "nodes_updated": updated,
                    "stale_flagged": len(stale)
                }
            })
            return {
                "updated": updated,
                "stale_flagged": len(stale),
                "stale_nodes": stale
            }
        except Exception as e:
            return {"error": str(e)}

    def get_stale_nodes(self, params: dict = {}) -> dict:
        if not self.connected:
            return {"stale": []}
        threshold = params.get("threshold", 0.3)
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Note)
                    WHERE n.temporal_weight IS NOT NULL
                    AND n.temporal_weight < $threshold
                    RETURN n.id as id,
                           n.aliases as aliases,
                           n.temporal_weight as tw,
                           n.captured as captured
                    ORDER BY n.temporal_weight ASC
                    LIMIT 20
                """, threshold=threshold)
                stale = [dict(r) for r in result]
            return {"stale": stale}
        except Exception as e:
            return {"error": str(e), "stale": []}
