from __future__ import annotations
import os
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
from clausebot_api.airtable_data_source import get_airtable_health
from clausebot_api.routes.quiz import router as quiz_router, DEFAULT_CATEGORY
from clausebot_api.routes.health import router as health_router

APP_NAME = os.getenv("APP_NAME", "clausebot-api")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

app = FastAPI(title=APP_NAME, version=APP_VERSION)

# Strict CORS - production domains only, no wildcards
ALLOWED_ORIGINS = [
    # Production domains
    "https://clausebot.miltmonndt.com",
    "https://clausebot.ai",  # Production domain
    "https://clausebot-api.onrender.com",
    # Development (local only)
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8081",
]

# Allow Vercel preview deployments (*.vercel.app)
# Note: In production, consider more restrictive patterns
env_origins = os.getenv("CORS_ALLOW_ORIGINS", "")
if env_origins:
    ALLOWED_ORIGINS.extend([x.strip() for x in env_origins.split(",") if x.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "Accept"],
    expose_headers=["X-Request-ID"],
)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "service": APP_NAME, "version": APP_VERSION}

@app.get("/health/airtable")
def airtable_health() -> Dict[str, Any]:
    return get_airtable_health()

# Primary mount
app.include_router(quiz_router, prefix="/v1", tags=["quiz"])

# Back-compat alias for legacy clients
app.include_router(quiz_router, prefix="/api", tags=["quiz-legacy"])

# Health diagnostics
app.include_router(health_router, tags=["health"])

@app.get("/health/quiz")
def quiz_health() -> Dict[str, Any]:
    return {"quiz": "ready", "default_category": DEFAULT_CATEGORY}

@app.on_event("startup")
async def startup_probe():
    try:
        from clausebot_api.routes.quiz import DEFAULT_CATEGORY as _dc
        print(f"[startup] quiz default category = {_dc}", flush=True)
    except Exception as e:
        print(f"[startup] quiz import failed: {e}", flush=True)
