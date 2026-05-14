from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
from utils import log_metrics, append_to_alerts

class Neo4jTraversal:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS),
                connection_timeout=10,
                max_connection_lifetime=300
            )
            self.driver.verify_connectivity()
            self.connected = True
        except Exception as e:
            print(f"Neo4j unavailable: {e}")
            self.connected = False

    def traverse(self, params: dict) -> dict:
        if not self.connected:
            return {"error": "Neo4j not connected", "nodes": []}
        seed_ids = params.get("seed_ids", [])
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Note)
                    RETURN n.id as id,
                           n.aliases as aliases,
                           coalesce(n.weight, 1.0) as weight,
                           coalesce(n.activation_count, 0) as activation,
                           coalesce(n.confidence, 'low') as confidence,
                           coalesce(n.status, 'active') as status,
                           coalesce(n.memory_tier, 'warm') as tier
                    ORDER BY weight DESC
                    LIMIT 15
                """)
                nodes = [dict(r) for r in result]
            log_metrics(f"traverse | returned:{len(nodes)}")
            return {"nodes": nodes}
        except Exception as e:
            return {"error": str(e), "nodes": []}

    def find_gaps(self, params: dict) -> dict:
        if not self.connected:
            return {"orphans": []}
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Note)
                    WHERE NOT (n)-[]-()
                    RETURN n.id as id,
                           n.aliases as aliases
                    LIMIT 20
                """)
                orphans = [dict(r) for r in result]
            return {"orphans": orphans}
        except Exception as e:
            return {"error": str(e), "orphans": []}

    def find_emergence(self, params: dict) -> dict:
        if not self.connected:
            return {"emergence_candidates": []}
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a:Note)-[]->(c:Note)<-[]-(b:Note)
                    WHERE a.id < b.id
                    AND NOT (a)-[]-(b)
                    RETURN a.id as node_a,
                           a.aliases as aliases_a,
                           b.id as node_b,
                           b.aliases as aliases_b,
                           count(c) as shared
                    ORDER BY shared DESC
                    LIMIT 5
                """)
                candidates = [dict(r) for r in result]
            return {"emergence_candidates": candidates}
        except Exception as e:
            return {"error": str(e), "emergence_candidates": []}

    def sync_node(self, params: dict) -> dict:
        if not self.connected:
            return {"status": "skipped", "reason": "neo4j not connected"}
        node_id = params.get("id", "")
        props = params.get("props", {})
        edges = params.get("edges", {})
        if not node_id:
            return {"error": "id required"}
        try:
            with self.driver.session() as session:
                session.run(
                    "MERGE (n:Note {id: $id}) SET n += $props",
                    id=str(node_id), props=props
                )
                for edge_type, targets in edges.items():
                    if not targets:
                        continue
                    if isinstance(targets, str):
                        targets = [targets]
                    for target in targets:
                        if not target:
                            continue
                        tid = str(target).replace(
                            "[[","").replace("]]","").strip()
                        if tid:
                            et = edge_type.upper().replace("-","_")
                            session.run(f"""
                                MATCH (a:Note {{id: $fid}})
                                MERGE (b:Note {{id: $tid}})
                                MERGE (a)-[:{et}]->(b)
                            """, fid=str(node_id), tid=tid)
            log_metrics(f"node_synced | id:{node_id}")
            return {"status": "synced", "id": node_id}
        except Exception as e:
            return {"error": str(e)}

    def run_inference(self, params: dict = {}) -> dict:
        if not self.connected:
            return {"status": "skipped"}
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (a:Note)-[:IMPLEMENTS]->(b:Note)
                          -[:REQUIRES]->(c:Note)
                    WHERE NOT (a)-[:REQUIRES]->(c)
                    AND a.id <> c.id
                    MERGE (a)-[:REQUIRES_INFERRED]->(c)
                """)
            log_metrics("inference_run | complete")
            return {"status": "complete"}
        except Exception as e:
            return {"error": str(e)}

    def get_tier_weighted_results(self, params: dict) -> dict:
        if not self.connected:
            return {"nodes": []}
        node_ids = params.get("node_ids", [])
        tier_weights = {
            "hot": 2.0, "warm": 1.5,
            "cool": 1.0, "cold": 0.3
        }
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Note)
                    RETURN n.id as id,
                           n.aliases as aliases,
                           coalesce(n.memory_tier,'warm') as tier,
                           coalesce(n.weight,1.0) as weight
                    LIMIT 15
                """)
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
