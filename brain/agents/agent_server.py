import asyncio
import json
import os
import sys
sys.path.insert(0, os.path.expanduser("~/Pandora/brain"))

from aiohttp import web
from config import AGENT_PORT

CARD = {
    "name": "pandora-brain",
    "version": "1.0.0",
    "description": "Pandora living second brain",
    "url": f"http://localhost:{AGENT_PORT}",
    "capabilities": {
        "capture":   "Process raw input into vault nodes",
        "retrieve":  "Answer questions from vault only",
        "research":  "Search arxiv and web for gaps",
        "synthesize":"Generate health reports",
        "maintain":  "Run self-healing and cleanup"
    },
    "protocols": ["MCP", "A2A"],
    "human_in_loop": True
}


async def handle_run(request):
    try:
        data = await request.json()
        user_input = data.get("input", "")
        return web.json_response({
            "status": "received",
            "input": user_input,
            "note": "LangGraph orchestrator coming in next phase"
        })
    except Exception as e:
        return web.json_response({"error": str(e)})


async def handle_card(request):
    return web.json_response(CARD)


async def handle_health(request):
    return web.json_response({"status": "alive"})


app = web.Application()
app.router.add_post("/run", handle_run)
app.router.add_get("/.well-known/agent-card.json", handle_card)
app.router.add_get("/health", handle_health)


if __name__ == "__main__":
    print(f"Pandora agent server on port {AGENT_PORT}")
    web.run_app(app, host="127.0.0.1", port=AGENT_PORT,
                print=None)
