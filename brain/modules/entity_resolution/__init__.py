from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS
from utils import log_metrics, write_module_health

class EntityResolver:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)
            )
            self.driver.verify_connectivity()
            self.connected = True
        except Exception as e:
            print(f"EntityResolver Neo4j unavailable: {e}")
            self.connected = False

    def find_and_merge_entities(self, params: dict = {}) -> dict:
        if not self.connected:
            return {"entities_resolved": 0}
        merged = 0
        pairs = []
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a:Note), (b:Note)
                    WHERE a.id < b.id
                    AND a.source <> b.source
                    AND any(alias IN a.aliases WHERE
                            alias IN b.aliases)
                    AND NOT (a)-[:SAME_ENTITY]-(b)
                    RETURN a.id as id_a,
                           a.aliases as aliases_a,
                           a.source as source_a,
                           b.id as id_b,
                           b.aliases as aliases_b,
                           b.source as source_b
                    LIMIT 20
                """)
                pairs = [dict(r) for r in result]

                for pair in pairs:
                    session.run("""
                        MATCH (a:Note {id: $id_a}),
                              (b:Note {id: $id_b})
                        MERGE (a)-[:SAME_ENTITY]-(b)
                    """, id_a=pair["id_a"], id_b=pair["id_b"])
                    merged += 1

            log_metrics(f"entity_resolution | merged:{merged}")
            write_module_health("entity-resolution", {
                "status": "healthy",
                "error_count": 0,
                "metrics": {"entities_merged": merged}
            })
            return {"entities_resolved": merged, "pairs": pairs}
        except Exception as e:
            return {"error": str(e), "entities_resolved": 0}
