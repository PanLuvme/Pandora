from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
from utils import log_metrics, write_module_health

class SpreadingActivation:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS),
                connection_timeout=10
            )
            self.driver.verify_connectivity()
            self.connected = True
        except Exception as e:
            print(f"SpreadingActivation Neo4j unavailable: {e}")
            self.connected = False

    def activate(self, params: dict) -> dict:
        if not self.connected:
            return {"activated_nodes": []}
        seed_ids = params.get("seed_ids", [])
        decay = params.get("decay", 0.7)
        threshold = params.get("threshold", 0.15)
        max_hops = params.get("max_hops", 4)

        if not seed_ids:
            return {"activated_nodes": [], "reason": "no seeds"}

        try:
            activated = []
            current_wave = {sid: 1.0 for sid in seed_ids}
            visited = set(seed_ids)

            for hop in range(max_hops):
                if not current_wave:
                    break
                next_wave = {}
                with self.driver.session() as session:
                    for node_id, activation in current_wave.items():
                        result = session.run("""
                            MATCH (n:Note {id: $id})-[]-(neighbor:Note)
                            WHERE neighbor.id NOT IN $visited
                            RETURN neighbor.id as id,
                                   neighbor.aliases as aliases,
                                   coalesce(neighbor.weight,1.0)
                                   as weight
                        """, id=node_id,
                            visited=list(visited))

                        for r in result:
                            nid = r["id"]
                            if not nid:
                                continue
                            new_activation = activation * decay
                            if new_activation >= threshold:
                                if nid not in next_wave or \
                                   next_wave[nid] < new_activation:
                                    next_wave[nid] = new_activation
                                visited.add(nid)
                                activated.append({
                                    "id": nid,
                                    "aliases": r["aliases"],
                                    "activation": round(
                                        new_activation, 3
                                    ),
                                    "hop": hop + 1
                                })

                        # Record co-activation
                        if len(seed_ids) > 1:
                            for other_id in seed_ids:
                                if other_id != node_id:
                                    session.run("""
                                        MATCH (a:Note {id: $a}),
                                              (b:Note {id: $b})
                                        MERGE (a)-[r:CO_ACTIVATED]-(b)
                                        ON CREATE SET r.count = 1
                                        ON MATCH SET
                                            r.count = r.count + 1
                                    """, a=node_id, b=other_id)

                current_wave = next_wave

            activated.sort(
                key=lambda x: x["activation"], reverse=True
            )
            log_metrics(
                f"spreading_activation | "
                f"seeds:{len(seed_ids)} "
                f"fired:{len(activated)}"
            )
            write_module_health("spreading-activation", {
                "status": "healthy",
                "error_count": 0,
                "metrics": {
                    "last_seeds": len(seed_ids),
                    "last_fired": len(activated)
                }
            })
            return {"activated_nodes": activated}
        except Exception as e:
            return {"error": str(e), "activated_nodes": []}

    def get_co_activations(self, params: dict) -> dict:
        if not self.connected:
            return {"co_activation_pairs": []}
        min_count = params.get("min_co_count", 3)
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a:Note)-[r:CO_ACTIVATED]-(b:Note)
                    WHERE r.count >= $min AND a.id < b.id
                    RETURN a.id as node_a,
                           b.id as node_b,
                           r.count as co_count
                    ORDER BY co_count DESC LIMIT 20
                """, min=min_count)
                pairs = [dict(r) for r in result]
            return {"co_activation_pairs": pairs}
        except Exception as e:
            return {"error": str(e), "co_activation_pairs": []}
