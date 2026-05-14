import os
import sys
import re
import frontmatter
sys.path.insert(0, os.path.expanduser("~/Pandora/brain"))

from config import VAULT_PATH, ATOMIC_PATH
from utils import log_metrics, wait_for_file_ready

def extract_frontmatter(content: str) -> dict:
    try:
        post = frontmatter.loads(content)
        return dict(post.metadata)
    except Exception:
        return {}

def sync_file(filepath: str):
    if not wait_for_file_ready(filepath):
        print(f"File locked, skipping: {filepath}")
        return
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        fm = extract_frontmatter(content)
        if not fm.get("id"):
            return
        node_id = str(fm["id"])
        props = {
            "aliases":         str(fm.get("aliases", "")),
            "strength":        fm.get("strength", "reference"),
            "confidence":      fm.get("confidence", "low"),
            "weight":          float(fm.get("weight", 1.0)),
            "activation_count":int(fm.get("activation_count", 0)),
            "status":          fm.get("status", "active"),
            "tags":            str(fm.get("tags", [])),
            "captured":        str(fm.get("captured", "")),
            "pheromone":       float(fm.get("pheromone", 0.0)),
            "temporal_weight": float(fm.get("temporal_weight", 1.0)),
            "surprise_score":  float(fm.get("surprise_score", 0.0)),
            "memory_tier":     fm.get("memory_tier", "warm"),
        }
        edges = fm.get("edges", {}) or {}
        log_metrics(f"node_synced | id:{node_id}")
        print(f"Synced: {node_id}")
    except Exception as e:
        print(f"Sync error for {filepath}: {e}")

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
