import time
import os
from datetime import datetime
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS, VAULT_PATH
from utils import log_metrics, write_module_health

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class PandoraSubconscious:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)
            )
            self.driver.verify_connectivity()
            self.connected = True
        except Exception as e:
            print(f"Subconscious Neo4j unavailable: {e}")
            self.connected = False
        self.loops_run = 0
        self.insights_generated = 0

    def run_single_loop(self, params: dict = {}) -> dict:
        if not self.connected:
            return {"status": "neo4j not connected"}
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Note)
                    WHERE n.status = 'active'
                    AND coalesce(n.activation_count, 0) >= 0
                    RETURN n.id as id, n.aliases as aliases,
                           coalesce(n.memory_tier,'warm') as tier
                    ORDER BY rand()
                    LIMIT 1
                """)
                seed = result.single()
                if not seed:
                    return {"status": "no_nodes"}

                seed_id = seed["id"]

                neighbors = session.run("""
                    MATCH (start:Note {id: $id})-[]-(neighbor:Note)
                    RETURN neighbor.id as id,
                           neighbor.aliases as aliases,
                           coalesce(neighbor.memory_tier,'warm') as tier
                    LIMIT 5
                """, id=seed_id)
                neighbor_ids = [r["id"] for r in neighbors if r["id"]]

                all_ids = [seed_id] + neighbor_ids
                if len(all_ids) < 2:
                    self.loops_run += 1
                    return {"status": "loop_complete", "seed": seed_id, "neighbors": 0}

                emergence = session.run("""
                    MATCH (a:Note)-[]->(common:Note)<-[]-(b:Note)
                    WHERE a.id IN $ids AND b.id IN $ids
                    AND a.id < b.id
                    AND NOT (a)-[]-(b)
                    WITH a, b, count(common) as shared
                    WHERE shared >= 2
                    RETURN a.id as node_a,
                           a.aliases as aliases_a,
                           b.id as node_b,
                           b.aliases as aliases_b,
                           shared
                    LIMIT 1
                """, ids=all_ids)

                emergence_found = emergence.single()
                self.loops_run += 1

                if emergence_found:
                    self.insights_generated += 1
                    self._write_insight(emergence_found, seed_id)
                    return {
                        "status": "emergence_detected",
                        "node_a": emergence_found["node_a"],
                        "node_b": emergence_found["node_b"],
                        "shared": emergence_found["shared"]
                    }

                if len(neighbor_ids) > 0:
                    for nid in neighbor_ids[:2]:
                        session.run("""
                            MATCH (a:Note {id: $a})-[r]-(b:Note {id: $b})
                            SET r.pheromone = coalesce(r.pheromone, 0) + 0.01
                        """, a=seed_id, b=nid)

                return {
                    "status": "loop_complete",
                    "seed": seed_id,
                    "neighbors": len(neighbor_ids)
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_burst(self, params: dict = {}) -> dict:
        n = params.get("loops", 50)
        results = {"loops": 0, "insights": 0, "errors": 0}
        for _ in range(n):
            result = self.run_single_loop()
            results["loops"] += 1
            if result.get("status") == "emergence_detected":
                results["insights"] += 1
            elif result.get("status") == "error":
                results["errors"] += 1
            time.sleep(0.01)
        write_module_health("subconscious", {
            "status": "healthy",
            "error_count": results["errors"],
            "metrics": {
                "total_loops": self.loops_run,
                "insights": self.insights_generated,
                "last_burst": n
            }
        })
        log_metrics(
            f"subconscious_burst | loops:{results['loops']} "
            f"insights:{results['insights']}"
        )
        return results

    def run_burst_adaptive(self, params: dict = {}) -> dict:
        if PSUTIL_AVAILABLE:
            cpu = psutil.cpu_percent(interval=1)
            if cpu > 70:
                return {"status": "paused", "reason": f"cpu:{cpu}%"}
            elif cpu > 40:
                loops = 20
            else:
                loops = 100
        else:
            loops = 50
        return self.run_burst({"loops": loops})

    def _write_insight(self, emergence: dict, seed_id: str):
        path = os.path.join(
            VAULT_PATH, "60_SelfImprovement",
            "SUBCONSCIOUS_INSIGHTS.md"
        )
        os.makedirs(os.path.dirname(path), exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = (
            f"\n## {ts}\n"
            f"**Detected:** {emergence['aliases_a']} "
            f"↔ {emergence['aliases_b']}\n"
            f"**Shared neighbors:** {emergence['shared']}\n"
            f"**Seed:** {seed_id}\n"
            f"**Action:** Bridge these concepts\n\n"
        )
        with open(path, "a") as f:
            f.write(entry)
