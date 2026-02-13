# main.py
# Unified API server — runs all bootcamp agents from one place.
# Run: uvicorn main:app --reload
# Docs: http://localhost:8000/docs

import importlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from settings import settings  # noqa: F401 — loads .env into os.environ

app = FastAPI(title="AI Agents Bootcamp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import all agent modules and include their routes
modules = [
    "02_structured_output",
    "03_tools_agent",
    "04_deps_agent",
    "05_streaming",
    "06_debate_arena",
    "07_agent_pipeline",
    "08_roast_my_code",
    "09_whisper_agent",
    "10_memory_chat",
]

for name in modules:
    mod = importlib.import_module(name)
    for route in mod.app.routes:
        if isinstance(route, APIRoute):
            route.tags = [name]
            app.router.routes.append(route)


@app.get("/", tags=["index"])
async def index():
    return {
        "message": "AI Agents Bootcamp API",
        "endpoints": {
            "POST /review": "Structured movie review (02)",
            "POST /ask": "Tools agent (03)",
            "POST /assist": "Deps + dynamic instructions (04)",
            "GET /story?topic=": "Streaming story (05)",
            "POST /debate": "Multi-agent debate (06)",
            "POST /blog": "Agent pipeline (07)",
            "POST /roast": "Code roaster (08)",
            "POST /transcribe": "Whisper + analysis (09)",
            "POST /chat": "Memory chat (10)",
            "GET /history/{session_id}": "Chat history (10)",
        },
        "docs": "/docs",
        "ui": "/ui",
    }


@app.get("/ui", tags=["index"])
async def ui_redirect():
    return RedirectResponse("/static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")
