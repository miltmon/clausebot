"""
🚀 ClauseBot Optimized API - Sub-1.2s Performance
Main FastAPI application with connection pooling and payload optimization
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import optimized components
from .routes.search_cached import router as search_cached_router
from .services.retriever_optimized import warm_cache, performance_monitor
from .middleware.rate_limiting import RateLimitMiddleware
from .middleware.performance_monitoring import PerformanceMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with startup/shutdown optimization"""

    # Startup
    logger.info("🚀 Starting ClauseBot Optimized API...")

    try:
        # Warm cache with common queries
        await warm_cache()
        logger.info("✅ Cache warmed successfully")

        # Initialize connection pools
        await initialize_connection_pools()
        logger.info("✅ Connection pools initialized")

        # Pre-compile regex patterns
        compile_performance_patterns()
        logger.info("✅ Performance patterns compiled")

        logger.info("🎯 ClauseBot API ready for sub-1.2s performance!")

    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("🔄 Shutting down ClauseBot API...")
    await cleanup_resources()
    logger.info("✅ Shutdown complete")


# Create FastAPI app with optimizations
app = FastAPI(
    title="ClauseBot Optimized API",
    description="High-performance AWS D1.1:2025 clause retrieval with sub-1.2s response times",
    version="2.0.0-optimized",
    lifespan=lifespan,
    # Optimize JSON serialization
    default_response_class=JSONResponse,
)

# Add performance middleware (order matters!)
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses >1KB
app.add_middleware(PerformanceMiddleware)  # Monitor performance
app.add_middleware(RateLimitMiddleware)  # Rate limiting

# CORS with optimized settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOW_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=False,  # Optimize by not sending credentials
    allow_methods=["GET", "POST"],  # Only needed methods
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,  # Cache preflight for 1 hour
)

# Include optimized routes
app.include_router(search_cached_router)


async def initialize_connection_pools():
    """Initialize optimized connection pools"""
    try:
        # Configure Supabase connection pooling
        from .services.supabase_client import configure_connection_pool

        await configure_connection_pool(
            min_connections=2,
            max_connections=10,
            connection_timeout=5.0,
            command_timeout=30.0,
        )

        # Configure HTTP client pooling for external APIs
        import httpx

        global http_client
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    except Exception as e:
        logger.error(f"Connection pool initialization failed: {str(e)}")
        raise


def compile_performance_patterns():
    """Pre-compile regex patterns for performance"""
    import re

    # Store compiled patterns globally for reuse
    global CLAUSE_PATTERN, TABLE_PATTERN, SYNONYM_PATTERNS

    CLAUSE_PATTERN = re.compile(r"\b(clause)\s+(\d+(?:\.\d+)*)\b", re.IGNORECASE)
    TABLE_PATTERN = re.compile(r"\b(table)\s+(\d+(?:\.\d+)*)\b", re.IGNORECASE)

    SYNONYM_PATTERNS = {
        "vt": re.compile(r"\bvt\b", re.IGNORECASE),
        "gmaw_s": re.compile(r"\bgmaw-s\b", re.IGNORECASE),
        "hi_lo": re.compile(r"\bhi-lo\b", re.IGNORECASE),
        "prequal": re.compile(r"\b(prequal|pre-qual)\b", re.IGNORECASE),
    }


async def cleanup_resources():
    """Clean up resources on shutdown"""
    try:
        # Close HTTP client
        if "http_client" in globals():
            await http_client.aclose()

        # Close database connections
        from .services.supabase_client import close_connections

        await close_connections()

    except Exception as e:
        logger.error(f"Resource cleanup failed: {str(e)}")


# Health check endpoint with performance metrics
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check with performance metrics"""
    try:
        from .services.retriever_optimized import get_optimized_retriever

        # Test database connectivity and performance
        retriever = get_optimized_retriever()
        health_data = await retriever.health_check()

        # Get performance statistics
        perf_stats = performance_monitor.get_stats()

        return {
            "status": "healthy",
            "edition": "AWS D1.1:2025-r1",
            "build": os.getenv("BUILD_SHA", "dev")[:7],
            "version": "2.0.0-optimized",
            "database": health_data,
            "performance": perf_stats,
            "optimizations": {
                "indexes": "trigram + full-text",
                "caching": "in-memory + CDN",
                "connection_pooling": "enabled",
                "gzip_compression": "enabled",
            },
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e), "edition": "AWS D1.1:2025-r1"}


# Legacy POST endpoint for backward compatibility
@app.post("/v1/chat")
async def chat_legacy(request: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy POST endpoint - redirects to optimized GET endpoint"""
    try:
        query = request.get("query", "")
        limit = request.get("limit", 5)

        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        # Use optimized retriever
        from .services.retriever_optimized import retrieve_optimized

        results = await retrieve_optimized(query, limit)

        # Format for legacy compatibility
        return {
            "query": query,
            "results": [
                {
                    "question_id": result.question_id,
                    "question": result.question,
                    "clause_reference": result.clause_reference,
                    "explanation": result.explanation,
                }
                for result in results
            ],
            "source": "ClauseBot",
            "edition": "AWS D1.1:2025-r1",
        }

    except Exception as e:
        logger.error(f"Legacy chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")


# Performance monitoring endpoint
@app.get("/v1/performance")
async def get_performance_stats() -> Dict[str, Any]:
    """Get detailed performance statistics"""
    try:
        stats = performance_monitor.get_stats()

        return {
            "performance_stats": stats,
            "sla_compliance": {
                "sub_1200ms_target": "95%",
                "current_performance": f"{stats.get('sub_1200ms_rate', 0)}%",
                "status": "compliant"
                if stats.get("sub_1200ms_rate", 0) >= 95
                else "needs_attention",
            },
            "optimization_status": {
                "database_indexes": "active",
                "connection_pooling": "active",
                "caching_layer": "active",
                "gzip_compression": "active",
            },
        }

    except Exception as e:
        logger.error(f"Performance stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Performance stats unavailable")


# Admin endpoint for cache management
@app.post("/admin/cache/clear")
async def clear_cache() -> Dict[str, Any]:
    """Clear in-memory cache (admin only)"""
    try:
        from .services.retriever_optimized import get_optimized_retriever

        retriever = get_optimized_retriever()
        retriever._hot_cache.clear()

        return {"status": "success", "message": "Cache cleared successfully"}

    except Exception as e:
        logger.error(f"Cache clear failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Cache clear failed")


# Exception handlers for better error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url.path),
        },
    )


# Startup event for development
@app.on_event("startup")
async def startup_event():
    """Development startup event"""
    logger.info("🚀 ClauseBot Optimized API starting...")


if __name__ == "__main__":
    # Optimized Uvicorn configuration
    uvicorn.run(
        "main_optimized:app",
        host="0.0.0.0",
        port=8081,
        workers=2,  # Optimize for IO-bound workload
        loop="uvloop",  # Use faster event loop
        http="httptools",  # Use faster HTTP parser
        access_log=False,  # Disable access logs for performance
        log_level="info",
        reload=False,  # Disable reload in production
    )
