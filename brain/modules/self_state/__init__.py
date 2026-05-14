import os
import json
from datetime import datetime
from neo4j import GraphDatabase
from config import (
    NEO4J_URI, NEO4J_USER, NEO4J_PASS,
    VAULT_PATH, REGISTRY_PATH
)
from utils import log_metrics, write_module_health

class SelfStateGenerator:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)
            )
            self.driver.verify_connectivity()
            self.connected = True
        except Exception as e:
            print(f"SelfState Neo4j unavailable: {e}")
            self.connected = False

    def generate(self, params: dict = {}) -> dict:
        state = {}

        if os.path.exists(REGISTRY_PATH):
            with open(REGISTRY_PATH) as f:
                registry = json.load(f)
            enabled = [
                {"id": mid, "name": m["name"], "layer": m["layer"]}
                for mid, m in registry.get("modules", {}).items()
                if m.get("enabled")
            ]
            disabled = [
                {"id": mid, "name": m["name"]}
                for mid, m in registry.get("modules", {}).items()
                if not m.get("enabled")
            ]
            state["enabled_modules"] = enabled
            state["disabled_modules"] = disabled

        if self.connected:
            try:
                with self.driver.session() as session:
                    r = session.run("""
                        MATCH (n:Note)
                        OPTIONAL MATCH (n)-[rel]-()
                        WITH n, count(rel) as degree
                        RETURN count(n) as total_nodes,
                               avg(degree) as avg_degree,
                               sum(CASE WHEN degree = 0
                                   THEN 1 ELSE 0 END) as orphans,
                               sum(CASE WHEN degree >= 5
                                   THEN 1 ELSE 0 END) as hubs
                    """)
                    stats = dict(r.single() or {})

                    domain_r = session.run("""
                        MATCH (n:Note)
                        UNWIND n.tags as tag
                        WHERE tag STARTS WITH 'Domain/'
                        RETURN tag as domain, count(*) as count
                        ORDER BY count DESC LIMIT 10
                    """)
                    domains = [dict(r) for r in domain_r]

                state["graph"] = {
                    "total_nodes": stats.get("total_nodes", 0),
                    "avg_connections": round(
                        float(stats.get("avg_degree") or 0), 2
                    ),
                    "hub_nodes": stats.get("hubs", 0),
                    "orphaned_nodes": stats.get("orphans", 0),
                    "domain_distribution": domains
                }
            except Exception as e:
                state["graph"] = {"error": str(e)}

        gaps = []
        total = state.get("graph", {}).get("total_nodes", 0)
        if total < 100:
            gaps.append("low node count — brain needs more captures")
        if state.get("graph", {}).get("orphaned_nodes", 0) > total * 0.15:
            gaps.append("high orphan rate — nodes need more edges")
        if float(state.get("graph", {}).get("avg_connections", 0)) < 2.0:
            gaps.append("low graph density — need better connectivity")

        disabled_ids = [m["id"] for m in state.get("disabled_modules", [])]
        if "causal-discovery" in disabled_ids:
            gaps.append("no causal structure detection")
        if "tda-gap-detection" in disabled_ids:
            gaps.append("no topological gap analysis")

        state["identified_gaps"] = gaps
        state["search_queries"] = self._gaps_to_queries(gaps)
        state["generated_at"] = datetime.now().isoformat()

        self._write_self_state(state)
        log_metrics(
            f"self_state_generated | "
            f"nodes:{state.get('graph',{}).get('total_nodes',0)} "
            f"gaps:{len(gaps)}"
        )
        write_module_health("self-state", {
            "status": "healthy",
            "error_count": 0,
            "metrics": {
                "gaps_identified": len(gaps),
                "nodes": state.get("graph", {}).get("total_nodes", 0)
            }
        })
        return state

    def _gaps_to_queries(self, gaps: list) -> list:
        queries = [
            "knowledge graph reasoning LLM 2025",
            "personal knowledge management AI agents 2025",
            "retrieval augmented generation improvement 2025"
        ]
        for gap in gaps:
            if "causal" in gap:
                queries.append("causal discovery knowledge graphs 2025")
            if "topological" in gap or "tda" in gap:
                queries.append("topological data analysis knowledge 2025")
            if "density" in gap or "connect" in gap:
                queries.append("knowledge graph link prediction 2025")
        seen = set()
        return [q for q in queries if not (q in seen or seen.add(q))][:8]

    def _write_self_state(self, state: dict):
        path = os.path.join(
            VAULT_PATH, "60_SelfImprovement", "SELF_STATE.md"
        )
        os.makedirs(os.path.dirname(path), exist_ok=True)
        content = f"# Brain self-state\nGenerated: {state['generated_at']}\n\n"
        content += f"## Graph\n"
        g = state.get("graph", {})
        content += f"- Total nodes: {g.get('total_nodes', 0)}\n"
        content += f"- Avg connections: {g.get('avg_connections', 0)}\n"
        content += f"- Hub nodes: {g.get('hub_nodes', 0)}\n"
        content += f"- Orphaned: {g.get('orphaned_nodes', 0)}\n\n"
        content += "## Identified gaps\n"
        for i, gap in enumerate(state.get("identified_gaps", []), 1):
            content += f"{i}. {gap}\n"
        content += "\n## Search queries\n"
        for q in state.get("search_queries", []):
            content += f"- {q}\n"
        with open(path, "w") as f:
            f.write(content)
