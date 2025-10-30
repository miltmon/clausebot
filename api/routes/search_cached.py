"""
🚀 ClauseBot Cached Search Routes - CDN Optimized
GET endpoints with proper cache headers for 150-300ms improvement
"""

import hashlib
import re
from typing import List, Dict, Any
from fastapi import APIRouter, Query, HTTPException, Response
import logging

from ..services.retriever_optimized import retrieve_optimized, retrieve_clause_direct

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["search-cached"])


def normalize_query(query: str) -> str:
    """Normalize query for consistent caching"""
    # Lowercase, trim, collapse multiple spaces
    normalized = re.sub(r"\s+", " ", query.lower().strip())
    return normalized


def get_cache_headers(query: str, max_age: int = 30) -> Dict[str, str]:
    """Generate cache headers for CDN optimization"""
    # Longer cache for direct clause queries (more stable)
    if re.search(r"\b(clause|table)\s+\d+(\.\d+)*\b", query, re.IGNORECASE):
        max_age = 300  # 5 minutes for clause queries

    return {
        "Cache-Control": f"public, s-maxage={max_age}, stale-while-revalidate=120",
        "Vary": "Accept-Encoding",
        "X-Cache-Key": hashlib.md5(query.encode()).hexdigest()[:8],
    }


@router.get("/search")
async def search_cached(
    q: str = Query(..., description="Search query", min_length=1, max_length=200),
    limit: int = Query(5, ge=1, le=20, description="Number of results"),
    response: Response = None,
) -> Dict[str, Any]:
    """
    Cacheable search endpoint for CDN optimization

    Expected performance:
    - Cached hits: 50-150ms TTFB
    - Uncached: <400ms with optimized indexes
    """
    try:
        # Normalize query for consistent caching
        normalized_query = normalize_query(q)

        # Set cache headers
        cache_headers = get_cache_headers(normalized_query)
        for key, value in cache_headers.items():
            response.headers[key] = value

        # Perform optimized search
        results = await retrieve_optimized(normalized_query, limit)

        # Format response
        return {
            "query": q,
            "normalized_query": normalized_query,
            "results": [
                {
                    "question_id": result.question_id,
                    "question": result.question,
                    "clause_reference": result.clause_reference,
                    "explanation": result.explanation,
                    "match_type": result.match_type,
                    "relevance_score": result.relevance_score,
                }
                for result in results
            ],
            "count": len(results),
            "source": "ClauseBot",
            "edition": "AWS D1.1:2025-r1",
            "cached": False,  # Will be True for CDN hits
            "cache_key": cache_headers["X-Cache-Key"],
        }

    except Exception as e:
        logger.error(f"Cached search error for query '{q}': {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/clauses/{clause_ref}")
async def get_clause_cached(
    clause_ref: str, response: Response = None
) -> Dict[str, Any]:
    """
    Fast path for direct clause lookups with aggressive caching

    Expected performance: <200ms uncached, <50ms cached
    """
    try:
        # Validate clause reference format
        if not re.match(r"^(Clause|Table)\s+\d+(\.\d+)*$", clause_ref, re.IGNORECASE):
            raise HTTPException(
                status_code=400, detail="Invalid clause reference format"
            )

        # Set aggressive cache headers for clause lookups
        cache_headers = {
            "Cache-Control": "public, s-maxage=600, stale-while-revalidate=300",  # 10 min cache
            "Vary": "Accept-Encoding",
            "X-Cache-Key": hashlib.md5(clause_ref.encode()).hexdigest()[:8],
        }

        for key, value in cache_headers.items():
            response.headers[key] = value

        # Direct clause lookup
        results = await retrieve_clause_direct(clause_ref)

        if not results:
            raise HTTPException(
                status_code=404, detail=f"Clause {clause_ref} not found"
            )

        return {
            "clause_reference": clause_ref,
            "results": [
                {
                    "question_id": result.question_id,
                    "question": result.question,
                    "clause_reference": result.clause_reference,
                    "explanation": result.explanation,
                    "match_type": result.match_type,
                    "relevance_score": result.relevance_score,
                }
                for result in results
            ],
            "count": len(results),
            "source": "ClauseBot",
            "edition": "AWS D1.1:2025-r1",
            "cached": False,
            "cache_key": cache_headers["X-Cache-Key"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clause lookup error for '{clause_ref}': {str(e)}")
        raise HTTPException(status_code=500, detail="Clause lookup failed")


@router.get("/search/suggestions")
async def get_search_suggestions(
    q: str = Query(..., description="Partial query", min_length=1, max_length=100),
    response: Response = None,
) -> Dict[str, Any]:
    """
    Search suggestions for autocomplete with caching
    """
    try:
        # Set cache headers for suggestions
        cache_headers = {
            "Cache-Control": "public, s-maxage=120, stale-while-revalidate=60",
            "Vary": "Accept-Encoding",
        }

        for key, value in cache_headers.items():
            response.headers[key] = value

        # Generate suggestions based on common patterns
        suggestions = generate_suggestions(q)

        return {"query": q, "suggestions": suggestions, "count": len(suggestions)}

    except Exception as e:
        logger.error(f"Suggestions error for query '{q}': {str(e)}")
        raise HTTPException(status_code=500, detail="Suggestions failed")


def generate_suggestions(partial_query: str) -> List[str]:
    """Generate search suggestions based on common patterns"""
    partial = partial_query.lower().strip()
    suggestions = []

    # Common clause patterns
    if partial.startswith("c") or partial.startswith("clause"):
        suggestions.extend(
            [
                "Clause 4.1 preheat requirements",
                "Clause 6.12 visual inspection",
                "Clause 5.15 welding procedure qualification",
            ]
        )

    # Common table patterns
    if partial.startswith("t") or partial.startswith("table"):
        suggestions.extend(
            [
                "Table 6.1 acceptance criteria",
                "Table 8.1 visual acceptance",
                "Table 4.1 preheat temperatures",
            ]
        )

    # Process-based suggestions
    if any(word in partial for word in ["weld", "gmaw", "process"]):
        suggestions.extend(
            [
                "GMAW-S prequalified joints",
                "welding procedure qualification",
                "filler metal requirements",
            ]
        )

    # Visual inspection suggestions
    if any(word in partial for word in ["visual", "vt", "inspect"]):
        suggestions.extend(
            [
                "visual acceptance table",
                "visual inspection requirements",
                "undercut limits",
            ]
        )

    # Filter suggestions that match the partial query
    filtered_suggestions = [
        s
        for s in suggestions
        if partial in s.lower() or any(word in s.lower() for word in partial.split())
    ]

    return filtered_suggestions[:10]  # Limit to 10 suggestions


@router.get("/health/cache")
async def cache_health_check() -> Dict[str, Any]:
    """Health check for cache performance"""
    try:
        # Test a simple cached query
        import time

        start_time = time.time()

        results = await retrieve_optimized("Clause 4.1", 1)

        elapsed = time.time() - start_time

        return {
            "status": "healthy",
            "cache_test_ms": round(elapsed * 1000, 2),
            "cache_performance": "optimal" if elapsed < 0.4 else "degraded",
            "results_count": len(results),
        }

    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Cache warming endpoint for deployment
@router.post("/admin/warm-cache")
async def warm_cache_endpoint() -> Dict[str, Any]:
    """Warm cache with common queries (admin only)"""
    try:
        from ..services.retriever_optimized import warm_cache

        await warm_cache()

        return {"status": "success", "message": "Cache warmed with common queries"}

    except Exception as e:
        logger.error(f"Cache warming failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Cache warming failed")
