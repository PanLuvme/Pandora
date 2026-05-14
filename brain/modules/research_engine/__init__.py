import os
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from config import VAULT_PATH
from utils import log_metrics, write_module_health

ARXIV_API = "http://export.arxiv.org/api/query"

class ResearchEngine:
    def __init__(self):
        self.papers_dir = os.path.join(
            VAULT_PATH, "60_SelfImprovement", "papers"
        )
        os.makedirs(self.papers_dir, exist_ok=True)

    def search_arxiv(self, params: dict) -> dict:
        queries = params.get("queries", [])
        max_per_query = params.get("max_per_query", 5)
        all_papers = []
        seen_ids = set()

        for query in queries[:6]:
            try:
                papers = self._query_arxiv(
                    query, max_per_query
                )
                for p in papers:
                    if p["arxiv_id"] not in seen_ids:
                        seen_ids.add(p["arxiv_id"])
                        all_papers.append(p)
                time.sleep(3)
            except Exception as e:
                print(f"Arxiv query failed: {query} — {e}")

        log_metrics(
            f"arxiv_search | "
            f"queries:{len(queries)} "
            f"found:{len(all_papers)}"
        )
        return {
            "papers": all_papers,
            "total": len(all_papers)
        }

    def _query_arxiv(self, query: str,
                     max_results: int) -> list:
        params = {
            "search_query": f"all:{query}",
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        r = requests.get(
            ARXIV_API, params=params, timeout=30
        )
        if r.status_code != 200:
            return []
        root = ET.fromstring(r.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        papers = []
        for entry in root.findall("atom:entry", ns):
            try:
                arxiv_id = entry.find(
                    "atom:id", ns
                ).text.split("/abs/")[-1]
                title = entry.find(
                    "atom:title", ns
                ).text.strip().replace("\n", " ")
                summary = entry.find(
                    "atom:summary", ns
                ).text.strip().replace("\n", " ")[:500]
                authors = [
                    a.find("atom:name", ns).text
                    for a in entry.findall(
                        "atom:author", ns
                    )[:3]
                ]
                published = entry.find(
                    "atom:published", ns
                ).text[:10]
                papers.append({
                    "arxiv_id": arxiv_id,
                    "title": title,
                    "summary": summary,
                    "authors": authors,
                    "published": published,
                    "url": f"https://arxiv.org/abs/{arxiv_id}",
                    "source_query": query
                })
            except Exception:
                continue
        return papers

    def evaluate_relevance(self, params: dict) -> dict:
        papers = params.get("papers", [])
        gaps = params.get("gaps", [])
        scored = []

        for paper in papers:
            score = self._score_paper(paper, gaps)
            if score["total"] > 0.3:
                scored.append({
                    **paper,
                    "relevance": score
                })

        scored.sort(
            key=lambda x: x["relevance"]["total"],
            reverse=True
        )
        return {
            "ranked_papers": scored[:15],
            "evaluated": len(papers),
            "relevant": len(scored)
        }

    def _score_paper(self, paper: dict,
                     gaps: list) -> dict:
        text = (
            paper["title"].lower() + " " +
            paper["summary"].lower()
        )
        year = int(paper["published"][:4])
        recency = (
            1.0 if year >= 2025 else
            0.8 if year >= 2024 else
            0.5 if year >= 2023 else 0.2
        )
        gap_keywords = {
            "retrieval": ["retrieval", "search", "rag"],
            "graph": ["knowledge graph", "graph neural"],
            "causal": ["causal", "causality"],
            "memory": ["memory", "continual learning"],
            "emergence": ["emergence", "analogy"],
            "topology": ["topological", "homology"],
            "compression": ["compression", "quantization"],
        }
        gap_score = 0.0
        for gap in gaps:
            for cat, keywords in gap_keywords.items():
                if any(kw in gap.lower() for kw in keywords):
                    if any(kw in text for kw in keywords):
                        gap_score = min(1.0, gap_score + 0.3)
                        break

        impl_keywords = [
            "algorithm", "framework", "implementation",
            "python", "open source", "code"
        ]
        impl_score = min(
            1.0,
            sum(0.2 for kw in impl_keywords if kw in text)
        )
        pkm_keywords = [
            "knowledge management", "knowledge graph",
            "personal knowledge", "memory", "retrieval"
        ]
        pkm_score = min(
            1.0,
            sum(0.25 for kw in pkm_keywords if kw in text)
        )
        total = (
            recency * 0.2 +
            gap_score * 0.4 +
            impl_score * 0.2 +
            pkm_score * 0.2
        )
        return {
            "recency": recency,
            "gap_alignment": gap_score,
            "implementability": impl_score,
            "pkm_relevance": pkm_score,
            "total": round(total, 3)
        }

    def write_findings(self, params: dict) -> dict:
        ranked = params.get("ranked_papers", [])
        evaluated = params.get("evaluated", 0)
        relevant = params.get("relevant", 0)

        findings_path = os.path.join(
            VAULT_PATH,
            "60_SelfImprovement",
            "ARXIV_FINDINGS.md"
        )
        content = (
            f"# Arxiv findings\n"
            f"Generated: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"Evaluated: {evaluated} | "
            f"Relevant: {relevant}\n\n"
            f"## Top candidates\n"
        )
        for i, paper in enumerate(ranked[:10], 1):
            score = paper["relevance"]["total"]
            content += (
                f"\n### {i}. {paper['title']}\n"
                f"- **URL:** {paper['url']}\n"
                f"- **Published:** {paper['published']}\n"
                f"- **Score:** {score:.2f}\n"
                f"- **Summary:** {paper['summary'][:200]}...\n"
            )

        with open(findings_path, "w") as f:
            f.write(content)

        queue_path = os.path.join(
            VAULT_PATH,
            "60_SelfImprovement",
            "IMPROVEMENT_QUEUE.md"
        )
        queue_content = (
            f"# Improvement queue\n"
            f"Updated: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"## Pending review\n"
        )
        for paper in ranked[:10]:
            score = paper["relevance"]["total"]
            priority = (
                "HIGH" if score > 0.7 else
                "MEDIUM" if score > 0.5 else "LOW"
            )
            queue_content += (
                f"\n- [ ] [{priority}] "
                f"**{paper['title'][:80]}**\n"
                f"  - Score: {score:.2f} | "
                f"{paper['published']}\n"
                f"  - {paper['url']}\n"
            )

        with open(queue_path, "w") as f:
            f.write(queue_content)

        write_module_health("research-engine", {
            "status": "healthy",
            "error_count": 0,
            "metrics": {
                "papers_found": len(ranked),
                "last_run": datetime.now().isoformat()
            }
        })
        log_metrics(
            f"research_findings | "
            f"papers:{len(ranked)}"
        )
        return {
            "findings_written": findings_path,
            "papers": len(ranked)
        }
