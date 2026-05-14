import math
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
from utils import log_metrics, append_to_alerts, write_module_health

class MDLPruning:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS),
                connection_timeout=10
            )
            self.driver.verify_connectivity()
            self.connected = True
        except Exception as e:
            print(f"MDLPruning Neo4j unavailable: {e}")
            self.connected = False

    def analyze(self, params: dict = {}) -> dict:
        if not self.connected:
            return {"redundant_nodes": []}
        threshold = params.get("threshold", 0.92)
        redundant = []
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Note)
                    OPTIONAL MATCH (n)-[]-(neighbor:Note)
                    WITH n,
                         count(neighbor) as neighbor_count,
                         coalesce(n.activation_count,0)
                         as activation
                    RETURN n.id as id,
                           n.aliases as aliases,
                           neighbor_count,
                           activation
                """)
                nodes = [dict(r) for r in result]

            for node in nodes:
                neighbor_count = node.get("neighbor_count") or 0
                activation = node.get("activation") or 0
                if neighbor_count < 2:
                    continue
                activation_penalty = 1 / math.log2(
                    2 + activation
                )
                redundancy = min(
                    0.99,
                    (neighbor_count /
                     max(1, neighbor_count + 1))
                    * activation_penalty
                )
                if redundancy > threshold:
                    redundant.append({
                        "id": node["id"],
                        "aliases": node["aliases"],
                        "redundancy": round(redundancy, 3),
                        "neighbor_count": neighbor_count
                    })

            if redundant:
                alert = (
                    f"\n## MDL redundancy candidates "
                    f"({len(redundant)} nodes)\n"
                )
                for r in redundant:
                    alert += (
                        f"- [ ] {r['id']} — "
                        f"{r['redundancy']:.0%} redundant\n"
                    )
                append_to_alerts(alert)

            log_metrics(
                f"mdl_pruning | "
                f"checked:{len(nodes)} "
                f"redundant:{len(redundant)}"
            )
            write_module_health("mdl-pruning", {
                "status": "healthy",
                "error_count": 0,
                "metrics": {
                    "nodes_checked": len(nodes),
                    "redundant_flagged": len(redundant)
                }
            })
            return {"redundant_nodes": redundant}
        except Exception as e:
            return {"error": str(e), "redundant_nodes": []}
