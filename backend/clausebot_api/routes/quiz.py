from typing import Optional, List, Dict, Any
import os
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from clausebot_api.airtable_data_source import get_questions
from clausebot_api.cache import cache, cache_key

router = APIRouter()

# Single source of truth for default; can override via env later if you want
DEFAULT_CATEGORY = "Structural Welding"

class QuizResponseItem(BaseModel):
    id: str
    q: str
    a: List[str]
    correct: str
    category: str
    clause_ref: str
    explanation: str
    source: str

class QuizResponse(BaseModel):
    count: int
    category: str
    source: str
    items: List[QuizResponseItem]

@router.get("/quiz", response_model=QuizResponse)
async def get_quiz(
    category: Optional[str] = Query(
        None,
        description="Airtable category (optional). Defaults to 'Structural Welding' if omitted."
    ),
    count: int = Query(5, ge=1, le=50, description="Number of questions to return"),
):
    """
    Get quiz questions with caching.
    
    Cache key format: cb:/v1/quiz:<category>:<count>
    Cache TTL: Configured via QUIZ_CACHE_TTL env (default 300s)
    
    On cache miss:
    - Fetches from Airtable
    - Stores in cache
    - Returns results
    
    On cache hit:
    - Returns cached results (sub-50ms)
    """
    
    cat = category or DEFAULT_CATEGORY

    try:
        # Generate cache key based on category and count
        key = cache_key("/v1/quiz", category=cat, count=count)
        
        # Define producer function for cache miss
        def fetch_quiz():
            items = get_questions(cat, count)
            if not items:
                # Surface as 422 (no records) rather than silent 503
                raise HTTPException(status_code=422, detail=f"No quiz records for category '{cat}' (need {count}, have 0)")
            return {"count": len(items), "category": cat, "source": "airtable", "items": items}
        
        # Get from cache or fetch (async-aware)
        result = await cache.get_or_set(key, fetch_quiz)
        
        return result

    except HTTPException:
        # Re-raise HTTPExceptions (like 422 from get_questions)
        raise
    
    except KeyError as e:
        # Likely missing env like AIRTABLE_API_KEY/BASE/TABLE
        detail = f"Configuration error: missing env {str(e)}"
        print(f"[quiz] {detail}", flush=True)
        raise HTTPException(status_code=500, detail=detail)

    except Exception as e:
        # Catch-all so we don't get opaque 503s
        detail = f"Quiz handler error: {type(e).__name__}: {str(e)}"
        print(f"[quiz] {detail}", flush=True)
        raise HTTPException(status_code=500, detail=detail)
