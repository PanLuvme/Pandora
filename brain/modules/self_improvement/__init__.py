import os
import json
import requests
from datetime import datetime
from config import VAULT_PATH, OLLAMA_URL, OLLAMA_MODEL
from utils import log_metrics, write_module_health

class SelfImprovementEvaluator:
    def __init__(self):
        self.queue_path = os.path.join(
            VAULT_PATH, "60_SelfImprovement",
            "IMPROVEMENT_QUEUE.md"
        )
        self.findings_path = os.path.join(
            VAULT_PATH, "60_SelfImprovement",
            "ARXIV_FINDINGS.md"
        )
        self.state_path = os.path.join(
            VAULT_PATH, "60_SelfImprovement",
            "SELF_STATE.md"
        )

    def evaluate_and_propose(self, params: dict = {}) -> dict:
        self_state = ""
        findings = ""
        queue = ""

        if os.path.exists(self.state_path):
            with open(self.state_path) as f:
                self_state = f.read()

        if os.path.exists(self.findings_path):
            with open(self.findings_path) as f:
                findings = f.read()

        if os.path.exists(self.queue_path):
            with open(self.queue_path) as f:
                queue = f.read()

        if not self_state and not findings:
            return {
                "error": "No self-state or findings found. "
                        "Run self-state and research-engine first."
            }

        proposals = self._generate_proposals(
            self_state, findings, queue
        )
        self._write_proposals(proposals)

        write_module_health("self-improvement", {
            "status": "healthy",
            "error_count": 0,
            "metrics": {
                "proposals_generated": len(
                    proposals.get("proposals", [])
                ),
                "last_run": datetime.now().isoformat()
            }
        })
        log_metrics(
            f"self_improvement | "
            f"proposals:{len(proposals.get('proposals',[]))}"
        )
        return proposals

    def _generate_proposals(self, self_state: str,
                             findings: str,
                             queue: str) -> dict:
        prompt = f"""You are analyzing a personal knowledge 
management system called Pandora that can add new Python 
modules to improve itself.

CURRENT BRAIN STATE:
{self_state[:1500]}

ARXIV FINDINGS:
{findings[:2000]}

Based on the brain gaps and research found, generate 3 
specific module proposals. For each:
1. Module ID (kebab-case)
2. What gap it solves
3. Which paper it implements
4. What it does in 2 sentences
5. Complexity: low/medium/high
6. Priority: high/medium/low

Respond ONLY in valid JSON:
{{
  "proposals": [
    {{
      "module_id": "string",
      "module_name": "string",
      "solves_gap": "string",
      "based_on": "string",
      "description": "string",
      "complexity": "low|medium|high",
      "priority": "high|medium|low"
    }}
  ],
  "health_assessment": "string",
  "next_action": "string"
}}"""

        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3}
                },
                timeout=120
            )
            text = r.json().get("response", "{}")
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except Exception as e:
            print(f"Proposal generation error: {e}")

        return {
            "proposals": [],
            "health_assessment": "evaluation failed — check Ollama",
            "next_action": "ensure Ollama is running"
        }

    def _write_proposals(self, proposals: dict):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        addition = f"\n\n## AI proposals ({ts})\n\n"
        addition += (
            f"**Health:** "
            f"{proposals.get('health_assessment','')}\n\n"
            f"**Next action:** "
            f"{proposals.get('next_action','')}\n\n"
        )
        for p in proposals.get("proposals", []):
            priority = p.get("priority","medium").upper()
            addition += (
                f"### [{priority}] {p.get('module_name','')}\n"
                f"- **ID:** `{p.get('module_id','')}`\n"
                f"- **Solves:** {p.get('solves_gap','')}\n"
                f"- **Based on:** {p.get('based_on','')}\n"
                f"- **Description:** {p.get('description','')}\n"
                f"- **Complexity:** {p.get('complexity','')}\n"
                f"- [ ] Approve [ ] Reject\n\n"
            )
        if os.path.exists(self.queue_path):
            with open(self.queue_path, "a") as f:
                f.write(addition)
        else:
            with open(self.queue_path, "w") as f:
                f.write(addition)
