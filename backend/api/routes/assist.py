"""
ClauseBot AI Assistant Routes
Provider-agnostic welding and NDT compliance assistance
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
from datetime import datetime

from ..model_router import llm_chat, get_available_providers

router = APIRouter(prefix="/api", tags=["AI Assistant"])


class AssistRequest(BaseModel):
    prompt: str = Field(
        ..., min_length=10, max_length=2000, description="User question or request"
    )
    context: Optional[str] = Field(
        None, max_length=5000, description="Additional context (code, standards, etc.)"
    )
    temperature: Optional[float] = Field(
        0.2, ge=0.0, le=1.0, description="Response creativity (0=focused, 1=creative)"
    )
    max_tokens: Optional[int] = Field(
        600, ge=50, le=2000, description="Maximum response length"
    )
    user_id: Optional[str] = Field(
        None, description="User identifier for usage tracking"
    )


class AssistResponse(BaseModel):
    ok: bool
    reply: str
    usage: Dict[str, Any]
    provider: str
    model: str
    timestamp: str


# Welding/NDT system prompt
CLAUSEBOT_SYSTEM_PROMPT = """You are ClauseBot, an expert AI assistant for welding and non-destructive testing (NDT) compliance.

Your expertise covers:
- AWS D1.1 Structural Welding Code
- ASME Section IX Welding and Brazing Qualifications  
- API standards for pipeline and pressure vessel welding
- CWI (Certified Welding Inspector) knowledge
- NDT methods: UT, RT, MT, PT, VT
- Welding procedures (WPS), qualifications (PQR), and welder certification
- Destructive testing and mechanical properties
- Metallurgy and heat treatment
- Safety standards and best practices

Guidelines:
- Provide accurate, code-compliant answers
- Reference specific standard sections when applicable
- Explain technical concepts clearly
- Always emphasize safety considerations
- If unsure about a specific requirement, recommend consulting the actual standard
- For complex procedures, suggest involving a qualified welding engineer or CWI

Keep responses concise but thorough. Focus on practical, actionable guidance."""


@router.post("/assist", response_model=AssistResponse)
async def assist(request: AssistRequest):
    """
    ClauseBot AI Assistant - Welding & NDT Compliance Help

    Provides expert guidance on welding codes, NDT procedures, and compliance requirements.
    Uses configurable AI providers (OpenAI, Anthropic, Google, Ollama) based on environment settings.
    """

    try:
        # Build conversation context
        messages = [{"role": "system", "content": CLAUSEBOT_SYSTEM_PROMPT}]

        # Add context if provided
        if request.context:
            context_message = (
                f"Additional context:\n{request.context}\n\nUser question:"
            )
            messages.append({"role": "user", "content": context_message})

        # Add user prompt
        messages.append({"role": "user", "content": request.prompt})

        # Call the model router
        response = await llm_chat(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            user_id=request.user_id,
            endpoint="/api/assist",
        )

        return AssistResponse(
            ok=True,
            reply=response.content,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "estimated_cost_usd": response.usage.estimated_cost_usd,
            },
            provider=response.provider,
            model=response.model,
            timestamp=response.usage.timestamp,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI assistance failed: {str(e)}")


@router.get("/assist/providers")
async def get_providers():
    """Get available AI providers and their configuration status"""
    return get_available_providers()


@router.post("/assist/batch")
async def assist_batch(requests: List[AssistRequest] = Body(..., max_items=5)):
    """
    Batch AI assistance for multiple questions
    Limited to 5 requests per batch to prevent abuse
    """

    if len(requests) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 requests per batch")

    try:
        # Process requests concurrently
        tasks = []
        for req in requests:
            # Create individual assist calls
            messages = [{"role": "system", "content": CLAUSEBOT_SYSTEM_PROMPT}]

            if req.context:
                context_message = (
                    f"Additional context:\n{req.context}\n\nUser question:"
                )
                messages.append({"role": "user", "content": context_message})

            messages.append({"role": "user", "content": req.prompt})

            task = llm_chat(
                messages=messages,
                temperature=req.temperature,
                max_tokens=req.max_tokens,
                user_id=req.user_id,
                endpoint="/api/assist/batch",
            )
            tasks.append(task)

        # Wait for all responses
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Format results
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                results.append(
                    {"ok": False, "error": str(response), "request_index": i}
                )
            else:
                results.append(
                    {
                        "ok": True,
                        "reply": response.content,
                        "usage": {
                            "input_tokens": response.usage.input_tokens,
                            "output_tokens": response.usage.output_tokens,
                            "estimated_cost_usd": response.usage.estimated_cost_usd,
                        },
                        "provider": response.provider,
                        "model": response.model,
                        "request_index": i,
                    }
                )

        # Calculate batch totals
        total_cost = sum(
            r.get("usage", {}).get("estimated_cost_usd", 0)
            for r in results
            if r.get("ok")
        )
        successful_requests = len([r for r in results if r.get("ok")])

        return {
            "batch_results": results,
            "summary": {
                "total_requests": len(requests),
                "successful": successful_requests,
                "failed": len(requests) - successful_requests,
                "total_estimated_cost_usd": round(total_cost, 6),
                "timestamp": datetime.now().isoformat(),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Batch processing failed: {str(e)}"
        )


@router.get("/assist/usage/summary")
async def usage_summary(
    days: int = Query(7, ge=1, le=30, description="Number of days to summarize"),
):
    """
    Get usage summary from Supabase model_usage table
    Shows cost and token usage over the specified period
    """

    try:
        from supabase import create_client
        import os
        from datetime import datetime, timedelta

        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not SUPABASE_URL or not SUPABASE_KEY:
            raise HTTPException(
                status_code=503, detail="Supabase not configured for usage tracking"
            )

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Query usage data
        result = (
            supabase.table("model_usage")
            .select("*")
            .gte("timestamp", start_date.isoformat())
            .lte("timestamp", end_date.isoformat())
            .execute()
        )

        if not result.data:
            return {
                "period_days": days,
                "total_requests": 0,
                "total_cost_usd": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "by_provider": {},
                "by_endpoint": {},
                "daily_breakdown": [],
            }

        # Aggregate data
        usage_data = result.data
        total_cost = sum(float(row["estimated_cost_usd"]) for row in usage_data)
        total_input_tokens = sum(row["input_tokens"] for row in usage_data)
        total_output_tokens = sum(row["output_tokens"] for row in usage_data)

        # Group by provider
        by_provider = {}
        for row in usage_data:
            provider = row["provider"]
            if provider not in by_provider:
                by_provider[provider] = {
                    "requests": 0,
                    "cost_usd": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                }
            by_provider[provider]["requests"] += 1
            by_provider[provider]["cost_usd"] += float(row["estimated_cost_usd"])
            by_provider[provider]["input_tokens"] += row["input_tokens"]
            by_provider[provider]["output_tokens"] += row["output_tokens"]

        # Group by endpoint
        by_endpoint = {}
        for row in usage_data:
            endpoint = row.get("endpoint", "unknown")
            if endpoint not in by_endpoint:
                by_endpoint[endpoint] = {"requests": 0, "cost_usd": 0.0}
            by_endpoint[endpoint]["requests"] += 1
            by_endpoint[endpoint]["cost_usd"] += float(row["estimated_cost_usd"])

        return {
            "period_days": days,
            "total_requests": len(usage_data),
            "total_cost_usd": round(total_cost, 4),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "by_provider": by_provider,
            "by_endpoint": by_endpoint,
            "average_cost_per_request": round(total_cost / len(usage_data), 4)
            if usage_data
            else 0.0,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Usage summary failed: {str(e)}")
