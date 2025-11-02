"""
Welding Resources API Routes
Provides Pro users access to curated welding symbols and CWI resources
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import os
from supabase import create_client, Client

router = APIRouter(prefix="/v1", tags=["welding-resources"])

# Pydantic models
class WeldingResource(BaseModel):
    """Welding resource article"""
    id: str
    url: str
    title: str
    description: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    category: str
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class WeldingResourcesList(BaseModel):
    """List of welding resources with metadata"""
    resources: List[WeldingResource]
    total: int
    category: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    welding_symbols_count: int
    cwi_resources_count: int
    total_count: int

# Supabase client initialization
def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration missing"
        )
    
    return create_client(url, key)

@router.get(
    "/welding-symbols",
    response_model=WeldingResourcesList,
    summary="Get Welding Symbols Articles",
    description="Returns curated articles about welding symbols and their usage. **Pro Feature**"
)
async def get_welding_symbols(
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Get welding symbols articles
    
    - **limit**: Maximum number of articles to return (1-100)
    - **offset**: Number of articles to skip for pagination
    """
    try:
        supabase = get_supabase_client()
        
        # Query welding symbols
        response = supabase.table("welding_resources")\
            .select("*")\
            .eq("category", "welding_symbols")\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        # Get total count
        count_response = supabase.table("welding_resources")\
            .select("id", count="exact")\
            .eq("category", "welding_symbols")\
            .execute()
        
        total = count_response.count or 0
        
        return WeldingResourcesList(
            resources=response.data,
            total=total,
            category="welding_symbols"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get(
    "/cwi-resources",
    response_model=WeldingResourcesList,
    summary="Get CWI Resources",
    description="Returns curated articles about AWS Certified Welding Inspector program and welding practices. **Pro Feature**"
)
async def get_cwi_resources(
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Get CWI resources articles
    
    - **limit**: Maximum number of articles to return (1-100)
    - **offset**: Number of articles to skip for pagination
    """
    try:
        supabase = get_supabase_client()
        
        # Query CWI resources
        response = supabase.table("welding_resources")\
            .select("*")\
            .eq("category", "cwi_resources")\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        # Get total count
        count_response = supabase.table("welding_resources")\
            .select("id", count="exact")\
            .eq("category", "cwi_resources")\
            .execute()
        
        total = count_response.count or 0
        
        return WeldingResourcesList(
            resources=response.data,
            total=total,
            category="cwi_resources"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get(
    "/welding-resources/search",
    response_model=WeldingResourcesList,
    summary="Search Welding Resources",
    description="Full-text search across all welding resources. **Pro Feature**"
)
async def search_welding_resources(
    q: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category: welding_symbols or cwi_resources"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Search welding resources by keyword
    
    - **q**: Search query (minimum 2 characters)
    - **category**: Optional filter by category
    - **limit**: Maximum number of results (1-100)
    - **offset**: Number of results to skip for pagination
    """
    try:
        supabase = get_supabase_client()
        
        # Build query
        query = supabase.table("welding_resources")\
            .select("*")\
            .text_search("title", q, config="english")\
            .order("created_at", desc=True)
        
        # Apply category filter if provided
        if category:
            if category not in ["welding_symbols", "cwi_resources"]:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid category. Must be 'welding_symbols' or 'cwi_resources'"
                )
            query = query.eq("category", category)
        
        # Execute with pagination
        response = query.range(offset, offset + limit - 1).execute()
        
        # Get total count (approximate for text search)
        count_query = supabase.table("welding_resources")\
            .select("id", count="exact")\
            .text_search("title", q, config="english")
        
        if category:
            count_query = count_query.eq("category", category)
        
        count_response = count_query.execute()
        total = count_response.count or 0
        
        return WeldingResourcesList(
            resources=response.data,
            total=total,
            category=category
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get(
    "/health/welding-resources",
    response_model=HealthResponse,
    summary="Welding Resources Health Check",
    description="Returns database statistics for welding resources"
)
async def welding_resources_health():
    """
    Health check for welding resources
    
    Returns count of articles by category
    """
    try:
        supabase = get_supabase_client()
        
        # Count welding symbols
        symbols_response = supabase.table("welding_resources")\
            .select("id", count="exact")\
            .eq("category", "welding_symbols")\
            .execute()
        
        # Count CWI resources
        cwi_response = supabase.table("welding_resources")\
            .select("id", count="exact")\
            .eq("category", "cwi_resources")\
            .execute()
        
        symbols_count = symbols_response.count or 0
        cwi_count = cwi_response.count or 0
        
        return HealthResponse(
            status="ok",
            welding_symbols_count=symbols_count,
            cwi_resources_count=cwi_count,
            total_count=symbols_count + cwi_count
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

