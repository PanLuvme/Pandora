import os
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASS, VAULT_PATH
from utils import log_metrics, write_module_health

class ActiveLearning:
    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS),
                connection_timeout=10
            )
            self.driver.verify_connectivity()
            self.connected = True
        except Exception as e:
            print(f"ActiveLearning Neo4j unavailable: {e}")
            self.connected = False

    def _epistemic_value(self, node_id: str) -> float:
        if not self.connected or not node_id:
            return 1.0
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Note {id: $id})
                    OPTIONAL MATCH (n)-[*1..2]-(neighbor:Note)
                    RETURN count(DISTINCT neighbor) as reachable,
                           n.activation_count as activation
                """, id=str(node_id))
                record = result.single()
            if not record:
                return 1.0
            reachable = record["reachable"] or 0
            activation = record["activation"] or 0
            return round(
                (reachable * 0.4) + (max(0, 5 - activation) * 0.6),
                2
            )
        except Exception:
            return 1.0

    def rank(self, params: dict = {}) -> dict:
        top_n = params.get("top_n", 3)
        oq_path = os.path.join(
            VAULT_PATH, "30_Projects", "OPEN_QUESTIONS.md"
        )
        if not os.path.exists(oq_path):
            return {"ranked_questions": [], "reason": "no open questions file"}

        with open(oq_path) as f:
            lines = f.readlines()

        questions = []
        for line in lines:
            line = line.strip()
            if not line.startswith("- [ ]"):
                continue
            parts = line.replace("- [ ]", "").strip().split("—")
            q_text = parts[0].strip()
            source_id = ""
            for part in parts:
                if "source:" in part:
                    source_id = part.replace(
                        "source:", ""
                    ).strip()
            if q_text:
                questions.append({
                    "question": q_text,
                    "source_id": source_id
                })

        scored = []
        for q in questions:
            value = self._epistemic_value(q["source_id"])
            scored.append({**q, "epistemic_value": value})

        scored.sort(
            key=lambda x: x["epistemic_value"], reverse=True
        )
        top = scored[:top_n]

        if top:
            priority_text = (
                "\n## Priority capture targets\n"
                "(ranked by epistemic value)\n\n"
            )
            for i, q in enumerate(top, 1):
                priority_text += (
                    f"{i}. [{q['epistemic_value']}] "
                    f"{q['question']}\n"
                )
            with open(oq_path, "a") as f:
                f.write(priority_text)

        log_metrics(
            f"active_learning | "
            f"questions:{len(questions)} top:{len(top)}"
        )
        write_module_health("active-learning", {
            "status": "healthy",
            "error_count": 0,
            "metrics": {
                "questions_ranked": len(questions),
                "top_returned": len(top)
            }
        })
        return {"ranked_questions": top}
