import os
import sys
sys.path.insert(0, os.path.expanduser("~/Pandora/brain"))

import frontmatter
from neo4j import GraphDatabase
from config import (
    ATOMIC_PATH, NEO4J_URI, NEO4J_USER, NEO4J_PASS
)
from utils import log_metrics, wait_for_file_ready

driver = GraphDatabase.driver(
    NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS)
)

def sync_file(filepath: str):
    if not wait_for_file_ready(filepath):
        print(f"File locked, skipping: {filepath}")
        return
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        post = frontmatter.loads(content)
        fm = dict(post.metadata)
        node_id = str(fm.get("id", ""))
        if not node_id:
            return
        props = {
            "aliases":         str(fm.get("aliases", "")),
            "confidence":      fm.get("confidence", "low"),
            "weight":          float(fm.get("weight", 1.0)),
            "activation_count":int(fm.get("activation_count", 0)),
            "status":          fm.get("status", "active"),
            "tags":            str(fm.get("tags", [])),
            "captured":        str(fm.get("captured", "")),
            "memory_tier":     fm.get("memory_tier", "warm"),
            "pheromone":       float(fm.get("pheromone", 0.0)),
            "temporal_weight": float(fm.get("temporal_weight", 1.0)),
        }
        edges = fm.get("edges", {}) or {}
        with driver.session() as session:
            session.run(
                "MERGE (n:Note {id: $id}) SET n += $props",
                id=node_id, props=props
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
                        """, fid=node_id, tid=tid)
        log_metrics(f"node_synced | id:{node_id}")
        print(f"Synced: {node_id}")
    except Exception as e:
        print(f"Error syncing {filepath}: {e}")

def sync_all():
    if not os.path.exists(ATOMIC_PATH):
        print(f"Atomic path not found: {ATOMIC_PATH}")
        return
    files = [
        f for f in os.listdir(ATOMIC_PATH)
        if f.endswith(".md")
    ]
    for filename in files:
        sync_file(os.path.join(ATOMIC_PATH, filename))
    print(f"Sync complete: {len(files)} files")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--file":
        sync_file(sys.argv[2])
    else:
        sync_all()
