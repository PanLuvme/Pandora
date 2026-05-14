import sys
import os
import json
sys.path.insert(0, os.path.expanduser("~/Pandora/brain"))

from registry import RegistryReader

registry = RegistryReader()
modules = {}

def load_enabled_modules():
    global modules
    modules = {}
    module_map = {
        "tiered-memory":       ("modules.tiered_memory",    "TieredMemory"),
        "subconscious":        ("modules.subconscious",     "PandoraSubconscious"),
        "semantic-dedup":      ("modules.semantic_dedup",   "SemanticDedup"),
        "entity-resolution":   ("modules.entity_resolution","EntityResolver"),
        "neo4j-traversal":     ("modules.neo4j_traversal",  "Neo4jTraversal"),
        "spreading-activation":("modules.spreading_activation","SpreadingActivation"),
        "temporal-decay":      ("modules.temporal_decay",   "TemporalDecay"),
        "stigmergic-memory":   ("modules.stigmergic_memory","StigmergicMemory"),
        "surprise-weighting":  ("modules.surprise_weighting","SurpriseWeighting"),
        "mdl-pruning":         ("modules.mdl_pruning",      "MDLPruning"),
        "active-learning":     ("modules.active_learning",  "ActiveLearning"),
        "conceptual-blending": ("modules.conceptual_blending","ConceptualBlending"),
        "tda-gap-detection":   ("modules.tda_gap_detection","TDAGapDetection"),
        "schema-abstraction":  ("modules.schema_abstraction","SchemaAbstraction"),
        "causal-discovery":    ("modules.causal_discovery", "CausalDiscovery"),
        "self-state":          ("modules.self_state",       "SelfStateGenerator"),
        "research-engine":     ("modules.research_engine",  "ResearchEngine"),
        "self-improvement":    ("modules.self_improvement", "SelfImprovementEvaluator"),
        "connectors":          ("modules.connectors",       "TelegramConnector"),
    }
    for module_id, (module_path, class_name) in module_map.items():
        if registry.is_enabled(module_id):
            try:
                import importlib
                mod = importlib.import_module(module_path)
                cls = getattr(mod, class_name)
                modules[module_id] = cls()
                print(f"Loaded: {module_id}", file=sys.stderr)
            except Exception as e:
                print(f"Failed to load {module_id}: {e}", file=sys.stderr)

load_enabled_modules()

def brain_tool(params: dict) -> dict:
    action = params.get("action")
    if action == "list":
        return {"enabled": registry.list_enabled()}
    elif action == "reload":
        registry.reload()
        load_enabled_modules()
        return {"status": "reloaded", "enabled": registry.list_enabled()}
    elif action == "load":
        return registry.get_schema(params.get("module", ""))
    elif action == "run":
        module_id = params.get("module")
        tool_name = params.get("tool")
        tool_params = params.get("params", {})
        if module_id not in modules:
            return {"error": f"{module_id} not enabled"}
        module = modules[module_id]
        if not hasattr(module, tool_name):
            return {"error": f"Tool {tool_name} not found"}
        return getattr(module, tool_name)(tool_params)
    return {"error": "action must be list, load, reload, or run"}

TOOL_MAP = {
    "brain_tool": brain_tool,
}

# MCP stdio protocol
def handle_message(msg: dict) -> dict:
    method = msg.get("method", "")
    msg_id = msg.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2025-11-25",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "pandora-brain",
                    "version": "1.0.0"
                }
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": [
                    {
                        "name": "brain_tool",
                        "description": "Interface to Pandora brain modules",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string"},
                                "module": {"type": "string"},
                                "tool": {"type": "string"},
                                "params": {"type": "object"}
                            },
                            "required": ["action"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        tool_name = msg.get("params", {}).get("name")
        tool_args = msg.get("params", {}).get("arguments", {})
        if tool_name in TOOL_MAP:
            result = TOOL_MAP[tool_name](tool_args)
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [{"type": "text", "text": json.dumps(result)}]
            }
        }
    elif method == "notifications/initialized":
        return None
    else:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }

def main():
    print("Pandora brain MCP server starting", file=sys.stderr)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            response = handle_message(msg)
            if response is not None:
                print(json.dumps(response), flush=True)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
