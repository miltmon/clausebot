# chat_compliance.py
# FastAPI router for RAG compliance endpoint (feature-flagged)
import os
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from clausebot_api.services import rag_service

router = APIRouter()

# Feature flag: RAG endpoint only active when enabled
RAG_ENABLED = os.getenv("RAG_ENABLED", "false").lower() == "true"

# Rate limiting (simple in-memory for single instance; use Redis for multi-instance)
from collections import defaultdict
from datetime import datetime, timedelta

request_counts = defaultdict(list)
RATE_LIMIT_PER_MINUTE = int(os.getenv("RAG_RATE_LIMIT_PER_MINUTE", "10"))

def check_rate_limit(client_id: str) -> bool:
    """Simple rate limiter: max N requests per minute per client"""
    now = datetime.utcnow()
    minute_ago = now - timedelta(minutes=1)
    
    # Clean old requests
    request_counts[client_id] = [
        ts for ts in request_counts[client_id] if ts > minute_ago
    ]
    
    # Check limit
    if len(request_counts[client_id]) >= RATE_LIMIT_PER_MINUTE:
        return False
    
    # Record this request
    request_counts[client_id].append(now)
    return True

# Request/Response models
class ComplianceChatRequest(BaseModel):
    query: str
    standard: Optional[str] = None
    top_k: int = 5
    session_id: Optional[str] = None

class CitationItem(BaseModel):
    clause_id: str
    standard: str
    section: str
    title: str
    similarity: float
    citation_text: str

class ComplianceChatResponse(BaseModel):
    answer: str
    citations: List[CitationItem]
    metadata: Dict
    session_id: str

@router.post("/chat/compliance", response_model=ComplianceChatResponse)
async def compliance_chat(req: ComplianceChatRequest):
    """
    RAG-powered compliance chat endpoint.
    
    Returns grounded answers with clause citations from AWS D1.1 and other standards.
    Requires RAG_ENABLED=true environment variable.
    """
    # Feature flag check
    if not RAG_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="RAG compliance endpoint is currently disabled. Set RAG_ENABLED=true to enable."
        )
    
    # Validation
    if not req.query or req.query.strip() == "":
        raise HTTPException(status_code=400, detail="query is required and cannot be empty")
    
    if req.top_k < 1 or req.top_k > 20:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 20")
    
    # Rate limiting (basic IP-based; enhance with auth tokens in production)
    # For now, use session_id as client identifier
    client_id = req.session_id or "anonymous"
    if not check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_PER_MINUTE} requests per minute."
        )
    
    # Generate session ID if not provided
    session_id = req.session_id or str(uuid.uuid4())
    
    # Execute RAG pipeline
    try:
        result = await rag_service.rag_pipeline(
            query=req.query,
            session_id=session_id,
            standard=req.standard,
            top_k=req.top_k
        )
        
        return ComplianceChatResponse(
            answer=result.get('answer', ''),
            citations=[CitationItem(**c) for c in result.get('citations', [])],
            metadata=result.get('metadata', {}),
            session_id=session_id
        )
    except Exception as e:
        print(f"RAG pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/chat/compliance/health")
async def compliance_health():
    """
    Health check for RAG compliance endpoint.
    
    Returns operational status and basic configuration checks.
    """
    try:
        # Check configuration
        openai_configured = bool(os.getenv("OPENAI_API_KEY"))
        supabase_configured = bool(os.getenv("SUPABASE_URL")) and bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
        
        # Quick DB check (sample query)
        clause_count = None
        try:
            result = rag_service.supabase.table('clause_embeddings').select('clause_id').limit(1).execute()
            clause_count = len(result.data) if result.data else 0
        except Exception as e:
            print(f"DB health check error: {e}")
        
        # Determine status
        if not openai_configured or not supabase_configured:
            status = "degraded"
        elif clause_count == 0:
            status = "no_data"
        else:
            status = "operational"
        
        return {
            "status": status,
            "rag_enabled": RAG_ENABLED,
            "openai_configured": openai_configured,
            "supabase_configured": supabase_configured,
            "clause_sample_available": clause_count is not None and clause_count > 0,
            "rate_limit_per_minute": RATE_LIMIT_PER_MINUTE
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

