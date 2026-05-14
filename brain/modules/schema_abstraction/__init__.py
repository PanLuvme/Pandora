import os
from datetime import datetime
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS, VAULT_PATH
from utils import log_metrics, write_module_health

class SchemaAbstraction:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS),
                connection_timeout=10
            )
            self.driver.verify_connectivity()
            self.connected = True
        except Exception as e:
            print(f"SchemaAbstraction Neo4j unavailable: {e}")
            self.connected = False

    def detect(self, params: dict = {}) -> dict:
        if not self.connected:
            return {"schema_candidates": []}
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a:Note), (b:Note), (c:Note)
                    WHERE a.id < b.id AND b.id < c.id
                    AND any(tag IN a.tags WHERE
                            tag IN b.tags
                            AND tag STARTS WITH 'Action/'
                            AND tag IN c.tags)
                    AND none(tag IN a.tags WHERE
                             tag STARTS WITH 'Domain/'
                             AND tag IN b.tags)
                    WITH a, b, c,
                         [tag IN a.tags WHERE
                          tag STARTS WITH 'Action/']
                         as shared_actions
                    RETURN a.id as id_a,
                           a.aliases as aliases_a,
                           b.id as id_b,
                           b.aliases as aliases_b,
                           c.id as id_c,
                           c.aliases as aliases_c,
                           shared_actions
                    LIMIT 5
                """)
                groups = [dict(r) for r in result]

            candidates = []
            for g in groups:
                candidates.append({
                    "nodes": [
                        {"id": g["id_a"],
                         "name": g["aliases_a"]},
                        {"id": g["id_b"],
                         "name": g["aliases_b"]},
                        {"id": g["id_c"],
                         "name": g["aliases_c"]}
                    ],
                    "shared_actions": g["shared_actions"],
                    "schema_question": (
                        f"What abstract pattern is shared by "
                        f"{g['aliases_a']}, {g['aliases_b']}, "
                        f"and {g['aliases_c']}?"
                    )
                })

            log_metrics(
                f"schema_abstraction | "
                f"candidates:{len(candidates)}"
            )
            write_module_health("schema-abstraction", {
                "status": "healthy",
                "error_count": 0,
                "metrics": {
                    "candidates_found": len(candidates)
                }
            })
            return {"schema_candidates": candidates}
        except Exception as e:
            return {"error": str(e), "schema_candidates": []}

    def match(self, params: dict) -> dict:
        if not self.connected:
            return {"matching_schemas": []}
        tags = params.get("node_tags", [])
        action_tags = [
            t for t in tags if t.startswith("Action/")
        ]
        if not action_tags:
            return {"matching_schemas": []}
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (s:Note {type: 'schema'})
                    WHERE any(tag IN s.tags
                              WHERE tag IN $tags)
                    RETURN s.id as id,
                           s.aliases as aliases
                    LIMIT 5
                """, tags=action_tags)
                schemas = [dict(r) for r in result]
            return {"matching_schemas": schemas}
        except Exception as e:
            return {"error": str(e), "matching_schemas": []}
