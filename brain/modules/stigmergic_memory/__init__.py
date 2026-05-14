import time
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
from utils import log_metrics, write_module_health

EVAPORATION_RATE = 0.05
DEPOSIT_AMOUNT = 1.0

class StigmergicMemory:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS),
                connection_timeout=10
            )
            self.driver.verify_connectivity()
            self.connected = True
        except Exception as e:
            print(f"StigmergicMemory Neo4j unavailable: {e}")
            self.connected = False

    def deposit(self, params: dict) -> dict:
        if not self.connected:
            return {"status": "skipped"}
        path_ids = params.get("path_node_ids", [])
        success = params.get("query_success", True)
        deposit = DEPOSIT_AMOUNT if success else -0.1
        if not path_ids:
            return {"status": "no path provided"}
        try:
            with self.driver.session() as session:
                for node_id in path_ids:
                    session.run("""
                        MATCH (n:Note {id: $id})
                        SET n.pheromone =
                            coalesce(n.pheromone, 0) + $dep
                    """, id=str(node_id), dep=deposit)
                for i in range(len(path_ids) - 1):
                    session.run("""
                        MATCH (a:Note {id: $a})-[r]-(b:Note {id: $b})
                        SET r.pheromone =
                            coalesce(r.pheromone, 0) + $dep
                    """, a=str(path_ids[i]),
                        b=str(path_ids[i+1]),
                        dep=deposit)
            log_metrics(
                f"pheromone_deposit | "
                f"nodes:{len(path_ids)} success:{success}"
            )
            return {"deposited": len(path_ids), "amount": deposit}
        except Exception as e:
            return {"error": str(e)}

    def evaporate(self, params: dict = {}) -> dict:
        if not self.connected:
            return {"status": "skipped"}
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (n:Note)
                    WHERE n.pheromone IS NOT NULL
                    SET n.pheromone = n.pheromone * (1 - $rate)
                """, rate=EVAPORATION_RATE)
                session.run("""
                    MATCH ()-[r]-()
                    WHERE r.pheromone IS NOT NULL
                    SET r.pheromone = r.pheromone * (1 - $rate)
                """, rate=EVAPORATION_RATE)
            log_metrics("pheromone_evaporation | daily")
            write_module_health("stigmergic-memory", {
                "status": "healthy",
                "error_count": 0,
                "metrics": {
                    "evaporation_rate": EVAPORATION_RATE
                }
            })
            return {"status": "evaporated",
                    "rate": EVAPORATION_RATE}
        except Exception as e:
            return {"error": str(e)}

    def retrieve(self, params: dict) -> dict:
        if not self.connected:
            return {"nodes": []}
        seed_ids = params.get("seed_ids", [])
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Note)
                    RETURN n.id as id,
                           n.aliases as aliases,
                           coalesce(n.weight, 1.0) as weight,
                           coalesce(n.pheromone, 0.0) as pheromone,
                           (coalesce(n.weight,1.0) * 0.6 +
                            coalesce(n.pheromone,0.0) * 0.4)
                           as score
                    ORDER BY score DESC
                    LIMIT 15
                """)
                nodes = [dict(r) for r in result]
            log_metrics(
                f"stigmergic_retrieve | "
                f"returned:{len(nodes)}"
            )
            return {"nodes": nodes}
        except Exception as e:
            return {"error": str(e), "nodes": []}
