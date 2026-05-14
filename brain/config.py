import os

# Base paths
BASE_PATH  = os.path.expanduser("~/Pandora")
BRAIN_PATH = os.path.expanduser("~/Pandora/brain")
VAULT_PATH = os.path.expanduser("~/Pandora/vault")

# Vault subfolders
ATOMIC_PATH           = os.path.join(VAULT_PATH, "10_Atomic")
INBOX_PATH            = os.path.join(VAULT_PATH, "00_Inbox")
DIAGNOSTICS_PATH      = os.path.join(VAULT_PATH, "70_Diagnostics")
SELF_IMPROVEMENT_PATH = os.path.join(VAULT_PATH, "60_SelfImprovement")
REGISTRY_PATH         = os.path.join(
    VAULT_PATH, "90_System", "modules", "REGISTRY.json"
)

# Neo4j
NEO4J_URI  = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "pandora2024"

# Ollama
OLLAMA_URL           = "http://localhost:11434"
OLLAMA_MODEL         = "llama3"
EMBEDDING_MODEL      = "mxbai-embed-large"
EMBEDDING_DIMENSIONS = 512

# Ports
MCP_PORT   = 8765
AGENT_PORT = 8766

# Daemon
DEBOUNCE_SECONDS = 3.0

# Memory tiers — hours before demotion
MEMORY_TIERS = {
    "hot":  {"max_age_hours": 24},
    "warm": {"max_age_hours": 168},
    "cool": {"max_age_hours": 720},
    "cold": {"max_age_hours": 99999}
}

# Subconscious
SUBCONSCIOUS_LOOPS_PER_BURST       = 100
SUBCONSCIOUS_CPU_THRESHOLD_PAUSE   = 70
SUBCONSCIOUS_CPU_THRESHOLD_REDUCED = 40
