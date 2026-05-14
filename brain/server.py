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
        "tiered-memory":        ("modules.tiered_memory",       "TieredMemory"),
        "subconscious":         ("modules.subconscious",        "PandoraSubconscious"),
        "semantic-dedup":       ("modules.semantic_dedup",      "SemanticDedup"),
        "entity-resolution":    ("modules.entity_resolution",   "EntityResolver"),
        "neo4j-traversal":      ("modules.neo4j_traversal",     "Neo4jTraversal"),
        "spreading-activation": ("modules.spreading_activation","SpreadingActivation"),
        "temporal-decay":       ("modules.temporal_decay",      "TemporalDecay"),
        "stigmergic-memory":    ("modules.stigmergic_memory",   "StigmergicMemory"),
        "surprise-weighting":   ("modules.surprise_weighting",  "SurpriseWeighting"),
        "mdl-pruning":          ("modules.mdl_pruning",         "MDLPruning"),
        "active-learning":      ("modules.active_learning",     "ActiveLearning"),
        "schema-abstraction":   ("modules.schema_abstraction",  "SchemaAbstraction"),
        "causal-discovery":     ("modules.causal_discovery",    "CausalDiscovery"),
        "self-state":           ("modules.self_state",          "SelfStateGenerator"),
        "research-engine":      ("modules.research_engine",     "ResearchEngine"),
        "self-improvement":     ("modules.self_improvement",    "SelfImprovementEvaluator"),
        "connectors":           ("modules.connectors",          "TelegramConnector"),
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
                print(f"Failed to load {module_id}: {e}",
                      file=sys.stderr)

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
    elif action == "write_note":
        import os
        from datetime import datetime
        # Check both top-level and nested params
        nested = params.get("params", {})
        note_id = (params.get("id") or
                   nested.get("id") or
                   datetime.now().strftime("%Y%m%d%H%M%S"))
        note_content = (params.get("content") or
                        params.get("note_content") or
                        params.get("markdown") or
                        nested.get("content") or
                        nested.get("note_content") or
                        nested.get("markdown") or "")
        folder = params.get("folder", "10_Atomic")
        filename = f"{note_id}.md"
        filepath = os.path.join(
            os.path.expanduser(f"~/Pandora/vault/{folder}"),
            filename
        )
        if not note_content:
            return {"error": "content required",
                    "received_keys": list(params.keys()),
                    "nested_keys": list(nested.keys())}
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(note_content)
        return {"status": "written", "path": filepath, "id": note_id}
    return {"error": "action must be list, load, reload, or run"}


TOOLS = [
    {
        "name": "brain_tool",
        "description": (
            "Interface to Pandora brain modules. "
            "Use action=list to see enabled modules, "
            "action=load to get schema, "
            "action=run to execute a module tool."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "list | load | reload | run | write_note"
                },
                "module": {
                    "type": "string",
                    "description": "module id e.g. neo4j-traversal"
                },
                "tool": {
                    "type": "string",
                    "description": "tool name e.g. traverse"
                },
                "params": {
                    "type": "object",
                    "description": "tool parameters"
                }
            },
            "required": ["action"]
        }
    }
]


def make_response(msg_id, result):
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": result
    }


def make_error(msg_id, code, message):
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": code, "message": message}
    }


def handle_message(msg: dict) -> dict | None:
    method = msg.get("method", "")
    msg_id = msg.get("id")

    if method == "initialize":
        return make_response(msg_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": False}
            },
            "serverInfo": {
                "name": "pandora-brain",
                "version": "1.0.0"
            }
        })

    elif method == "notifications/initialized":
        return None

    elif method == "ping":
        return make_response(msg_id, {})

    elif method == "tools/list":
        return make_response(msg_id, {"tools": TOOLS})

    elif method == "tools/call":
        params = msg.get("params", {})
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})

        if tool_name == "brain_tool":
            try:
                result = brain_tool(tool_args)
                return make_response(msg_id, {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }],
                    "isError": False
                })
            except Exception as e:
                return make_response(msg_id, {
                    "content": [{
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }],
                    "isError": True
                })
        else:
            return make_error(
                msg_id, -32601,
                f"Tool not found: {tool_name}"
            )

    elif method == "resources/list":
        return make_response(msg_id, {"resources": []})

    elif method == "prompts/list":
        return make_response(msg_id, {"prompts": []})

    else:
        if msg_id is not None:
            return make_error(
                msg_id, -32601,
                f"Method not found: {method}"
            )
        return None


def main():
    print("Pandora brain MCP server starting",
          file=sys.stderr)
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            response = handle_message(msg)
            if response is not None:
                print(json.dumps(response),
                      flush=True)
        except json.JSONDecodeError as e:
            print(f"JSON error: {e}", file=sys.stderr)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
# This will be added inside brain_tool function
