import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.expanduser("~/Pandora/brain"))

from registry import RegistryReader
from config import MCP_PORT

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
                print(
                    f"Failed to load {module_id}: {e}",
                    file=sys.stderr
                )

load_enabled_modules()


def brain_tool(params: dict) -> dict:
    action = params.get("action")
    if action == "list":
        return {"enabled": registry.list_enabled()}
    elif action == "reload":
        registry.reload()
        load_enabled_modules()
        return {"status": "reloaded",
                "enabled": registry.list_enabled()}
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
    "brain_tool": lambda p: brain_tool(p),
}


async def handle_request(reader, writer):
    try:
        data = await reader.readline()
        if not data:
            writer.close()
            return
        request = json.loads(data.decode().strip())
        tool = request.get("tool")
        params = request.get("params", {})
        if tool in TOOL_MAP:
            result = TOOL_MAP[tool](params)
        else:
            result = {
                "error": f"Unknown tool: {tool}",
                "available": list(TOOL_MAP.keys())
            }
    except Exception as e:
        result = {"error": str(e)}
    writer.write((json.dumps(result) + "\n").encode())
    await writer.drain()
    writer.close()


async def main():
    server = await asyncio.start_server(
        handle_request, "127.0.0.1", MCP_PORT
    )
    handshake = {
        "name": "pandora-brain",
        "version": "1.0.0",
        "tools": list(TOOL_MAP.keys()),
    }
    print(json.dumps(handshake))
    sys.stdout.flush()
    print(
        f"Pandora MCP server running on port {MCP_PORT}",
        file=sys.stderr
    )
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
