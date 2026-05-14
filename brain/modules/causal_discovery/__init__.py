from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
from utils import log_metrics, write_module_health

class CausalDiscovery:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS),
                connection_timeout=10
            )
            self.driver.verify_connectivity()
            self.connected = True
        except Exception as e:
            print(f"CausalDiscovery Neo4j unavailable: {e}")
            self.connected = False

    def discover(self, params: dict = {}) -> dict:
        if not self.connected:
            return {"causal_edges": []}
        min_obs = params.get("min_observations", 3)
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a:Note)-[r:CO_ACTIVATED]-(b:Note)
                    WHERE r.count >= $min
                    AND a.id < b.id
                    AND coalesce(a.activation_count,0) >
                        coalesce(b.activation_count,0)
                    RETURN a.id as cause,
                           a.aliases as cause_name,
                           b.id as effect,
                           b.aliases as effect_name,
                           r.count as strength
                    ORDER BY strength DESC LIMIT 20
                """, min=min_obs)
                edges = [dict(r) for r in result]

                for edge in edges:
                    session.run("""
                        MATCH (a:Note {id: $cause}),
                              (b:Note {id: $effect})
                        MERGE (a)-[:CAUSES {
                            strength: $strength
                        }]->(b)
                    """, cause=edge["cause"],
                        effect=edge["effect"],
                        strength=edge["strength"])

            log_metrics(
                f"causal_discovery | "
                f"edges_found:{len(edges)}"
            )
            write_module_health("causal-discovery", {
                "status": "healthy",
                "error_count": 0,
                "metrics": {"causal_edges": len(edges)}
            })
            return {"causal_edges": edges}
        except Exception as e:
            return {"error": str(e), "causal_edges": []}

    def get_root_causes(self, params: dict) -> dict:
        if not self.connected:
            return {"root_causes": []}
        node_id = params.get("node_id")
        if not node_id:
            return {"error": "node_id required"}
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH path = (root:Note)
                        -[:CAUSES*1..5]->
                        (target:Note {id: $id})
                    WHERE NOT ()-[:CAUSES]->(root)
                    RETURN root.id as id,
                           root.aliases as aliases,
                           length(path) as distance
                    ORDER BY distance ASC LIMIT 10
                """, id=str(node_id))
                roots = [dict(r) for r in result]
            return {"root_causes": roots}
        except Exception as e:
            return {"error": str(e), "root_causes": []}
