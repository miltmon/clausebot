"""
ClauseBot API - Enhanced with Superpowers
Dual-database persistence, AI assistance, cost monitoring, and security
"""
import os
import json
import uuid
import time
from typing import Optional, List, Literal, Any, Dict

from fastapi import FastAPI, HTTPException, Query, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from supabase import create_client, Client
import httpx

# Import security middleware
from security import SecurityMiddleware, config as security_config, get_request_id

# Import new superpower routes
from api.routes.assist import router as assist_router
from api.routes.costs import router as costs_router
from api.routes.quiz import router as quiz_router
from api.routes.airtable_health import router as airtable_health_router
from api.routes.airtable_sample import router as airtable_sample_router
from api.routes.quiz_wrapped import router as quiz_wrapped_router

# Load environment variables with defaults for development
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hqhughgdraokwmreronk.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
AIRTABLE_TABLE_DEFAULT = os.getenv("AIRTABLE_TABLE_DEFAULT", "incidents")

ALLOWED_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "").split(",") if os.getenv("CORS_ALLOW_ORIGINS") else [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:8080",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5173"
]

# Initialize FastAPI with metadata including version info
app = FastAPI(
    title="ClauseBot API",
    description="Dual-database API for ClauseBot with AI assistance and monitoring",
    version=security_config.app_version,
    docs_url="/docs" if not security_config.robots_noindex_docs else None,
    redoc_url="/redoc" if not security_config.robots_noindex_docs else None,
)

# Add security middleware FIRST (before CORS)
app.add_middleware(SecurityMiddleware)

# Configure CORS with tighter controls
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-App-Version"],
)

# Initialize clients
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Warning: Supabase client initialization failed: {e}")
    supabase = None

# --- Base Models (Schemas) ---

class QuestionRequest(BaseModel):
    question: str = Field(..., description="The question text to search for")
    tags: Optional[List[str]] = Field(default=None, description="Optional list of tags to filter by")
    strict_tag_match: bool = Field(default=False, description="If True, all tags must match")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query text")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")

class Question(BaseModel):
    id: str
    question: str
    answer: str
    tags: Optional[List[str]] = None
    airtable_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    feature_public: bool
    supabase_connected: bool
    airtable_configured: bool

# --- Routes ---

@app.get("/", tags=["Health"])
async def root(request: Request):
    """Root endpoint with basic info and feature flag status."""
    return {
        "message": "ClauseBot API is running",
        "version": security_config.app_version,
        "feature_public": security_config.feature_public,
        "docs": "/docs" if not security_config.robots_noindex_docs else "disabled",
        "request_id": get_request_id(request)
    }

@app.get("/health", tags=["Health"], response_model=HealthResponse)
async def health_check(request: Request):
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        version=security_config.app_version,
        feature_public=security_config.feature_public,
        supabase_connected=supabase is not None,
        airtable_configured=bool(AIRTABLE_API_KEY and AIRTABLE_BASE_ID)
    )

@app.get("/status", tags=["Health"])
async def status_check(request: Request):
    """Internal status page with feature flags and build info."""
    # This endpoint should be protected in production
    return {
        "app": security_config.app_name,
        "version": security_config.app_version,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "feature_flags": {
            "public": security_config.feature_public,
            "api_key_required": security_config.api_key_required,
            "robots_noindex_preview": security_config.robots_noindex_preview,
            "robots_noindex_docs": security_config.robots_noindex_docs,
        },
        "rate_limit": {
            "per_minute": security_config.rate_limit_per_minute,
        },
        "security": {
            "ip_allowlist_enabled": bool(security_config.ip_allowlist),
        },
        "request_id": get_request_id(request)
    }

# --- Supabase Routes ---

@app.get("/v1/questions", tags=["Questions"])
async def list_questions(
    request: Request,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    List all questions from Supabase with pagination.
    Protected by feature flag and API key authentication.
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        response = supabase.table("questions").select("*").range(offset, offset + limit - 1).execute()
        return {
            "data": response.data,
            "count": len(response.data),
            "request_id": get_request_id(request)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching questions: {str(e)}")

@app.post("/v1/questions/search", tags=["Questions"])
async def search_questions(request: Request, search_request: SearchRequest):
    """
    Search questions using full-text search in Supabase.
    Protected by feature flag and API key authentication.
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        response = supabase.table("questions").select("*").text_search(
            "question", search_request.query
        ).limit(search_request.limit).execute()
        
        return {
            "query": search_request.query,
            "results": response.data,
            "count": len(response.data),
            "request_id": get_request_id(request)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching questions: {str(e)}")

@app.get("/v1/questions/{question_id}", tags=["Questions"])
async def get_question(request: Request, question_id: str):
    """
    Get a specific question by ID from Supabase.
    Protected by feature flag and API key authentication.
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase connection not available")
    
    try:
        response = supabase.table("questions").select("*").eq("id", question_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return {
            "data": response.data[0],
            "request_id": get_request_id(request)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching question: {str(e)}")

# --- Include routers for superpowers ---
app.include_router(assist_router, prefix="/v1", tags=["AI Assist"])
app.include_router(costs_router, prefix="/v1", tags=["Cost Monitoring"])
app.include_router(quiz_router, prefix="/v1", tags=["Quiz"])
app.include_router(airtable_health_router, prefix="/v1", tags=["Airtable"])
app.include_router(airtable_sample_router, prefix="/v1", tags=["Airtable"])
app.include_router(quiz_wrapped_router, prefix="/v1", tags=["Quiz Wrapped"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8081"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting ClauseBot API v{security_config.app_version}")
    print(f"Feature public: {security_config.feature_public}")
    print(f"API key required: {security_config.api_key_required}")
    print(f"Rate limit: {security_config.rate_limit_per_minute} req/min")
    
    uvicorn.run(app, host=host, port=port)
