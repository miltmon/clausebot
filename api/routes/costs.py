"""
ClauseBot Cost Estimation Routes
Monitor and estimate AI model usage costs
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict
from datetime import datetime, timedelta
import os

from ..model_router import COST_PER_1K_TOKENS

router = APIRouter(prefix="/api/costs", tags=["Cost Management"])


class CostEstimateRequest(BaseModel):
    provider_model: str = Field(
        ..., description="Model identifier (e.g., 'gpt-4', 'claude-3-sonnet')"
    )
    monthly_calls: int = Field(
        ..., ge=1, le=1000000, description="Expected calls per month"
    )
    avg_input_tokens: int = Field(
        ..., ge=10, le=10000, description="Average input tokens per call"
    )
    avg_output_tokens: int = Field(
        ..., ge=10, le=10000, description="Average output tokens per call"
    )


class CostEstimateResponse(BaseModel):
    provider_model: str
    monthly_calls: int
    avg_input_tokens: int
    avg_output_tokens: int
    cost_per_call_usd: float
    monthly_cost_usd: float
    yearly_cost_usd: float
    cost_breakdown: Dict[str, float]
    timestamp: str


@router.post("/estimate", response_model=CostEstimateResponse)
async def estimate_costs(request: CostEstimateRequest):
    """
    Estimate monthly and yearly costs for AI model usage

    Provides detailed cost breakdown for planning and budgeting.
    Supports all major providers: OpenAI, Anthropic, Google, Ollama.
    """

    # Validate model exists in our cost database
    if request.provider_model not in COST_PER_1K_TOKENS:
        available_models = list(COST_PER_1K_TOKENS.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Model '{request.provider_model}' not found. Available models: {available_models}",
        )

    # Calculate costs
    model_costs = COST_PER_1K_TOKENS[request.provider_model]

    input_cost_per_call = (request.avg_input_tokens / 1000) * model_costs["input"]
    output_cost_per_call = (request.avg_output_tokens / 1000) * model_costs["output"]
    total_cost_per_call = input_cost_per_call + output_cost_per_call

    monthly_cost = total_cost_per_call * request.monthly_calls
    yearly_cost = monthly_cost * 12

    return CostEstimateResponse(
        provider_model=request.provider_model,
        monthly_calls=request.monthly_calls,
        avg_input_tokens=request.avg_input_tokens,
        avg_output_tokens=request.avg_output_tokens,
        cost_per_call_usd=round(total_cost_per_call, 6),
        monthly_cost_usd=round(monthly_cost, 2),
        yearly_cost_usd=round(yearly_cost, 2),
        cost_breakdown={
            "input_cost_per_call": round(input_cost_per_call, 6),
            "output_cost_per_call": round(output_cost_per_call, 6),
            "input_cost_monthly": round(input_cost_per_call * request.monthly_calls, 2),
            "output_cost_monthly": round(
                output_cost_per_call * request.monthly_calls, 2
            ),
        },
        timestamp=datetime.now().isoformat(),
    )


@router.get("/models")
async def get_model_pricing():
    """
    Get current pricing for all supported models

    Returns per-1K-token pricing for input and output tokens.
    Prices are approximate and may vary by provider.
    """

    return {
        "pricing_per_1k_tokens": COST_PER_1K_TOKENS,
        "currency": "USD",
        "note": "Prices are approximate and may vary. Check provider documentation for exact pricing.",
        "last_updated": "2024-10-01",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/compare")
async def compare_models(
    monthly_calls: int = Query(
        ..., ge=1, le=1000000, description="Expected calls per month"
    ),
    avg_input_tokens: int = Query(
        ..., ge=10, le=10000, description="Average input tokens per call"
    ),
    avg_output_tokens: int = Query(
        ..., ge=10, le=10000, description="Average output tokens per call"
    ),
):
    """
    Compare costs across all available models

    Helps choose the most cost-effective model for your usage pattern.
    """

    comparisons = []

    for model_name, costs in COST_PER_1K_TOKENS.items():
        input_cost_per_call = (avg_input_tokens / 1000) * costs["input"]
        output_cost_per_call = (avg_output_tokens / 1000) * costs["output"]
        total_cost_per_call = input_cost_per_call + output_cost_per_call
        monthly_cost = total_cost_per_call * monthly_calls

        comparisons.append(
            {
                "model": model_name,
                "cost_per_call_usd": round(total_cost_per_call, 6),
                "monthly_cost_usd": round(monthly_cost, 2),
                "yearly_cost_usd": round(monthly_cost * 12, 2),
                "provider": model_name.split("-")[0]
                if "-" in model_name
                else "unknown",
            }
        )

    # Sort by monthly cost
    comparisons.sort(key=lambda x: x["monthly_cost_usd"])

    return {
        "usage_parameters": {
            "monthly_calls": monthly_calls,
            "avg_input_tokens": avg_input_tokens,
            "avg_output_tokens": avg_output_tokens,
        },
        "model_comparisons": comparisons,
        "cheapest_model": comparisons[0]["model"] if comparisons else None,
        "most_expensive_model": comparisons[-1]["model"] if comparisons else None,
        "cost_range_monthly": {
            "min": comparisons[0]["monthly_cost_usd"] if comparisons else 0,
            "max": comparisons[-1]["monthly_cost_usd"] if comparisons else 0,
        },
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/actual")
async def get_actual_costs(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
):
    """
    Get actual costs from usage logs

    Analyzes real usage data from Supabase to show actual spending.
    """

    try:
        from supabase import create_client

        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not SUPABASE_URL or not SUPABASE_KEY:
            raise HTTPException(
                status_code=503, detail="Supabase not configured for cost tracking"
            )

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Query actual usage
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
                "total_cost_usd": 0.0,
                "total_requests": 0,
                "daily_average_cost": 0.0,
                "projected_monthly_cost": 0.0,
                "by_model": {},
                "by_provider": {},
                "cost_trend": [],
            }

        usage_data = result.data

        # Calculate totals
        total_cost = sum(float(row["estimated_cost_usd"]) for row in usage_data)
        total_requests = len(usage_data)
        daily_average = total_cost / days if days > 0 else 0
        projected_monthly = daily_average * 30

        # Group by model
        by_model = {}
        for row in usage_data:
            model = row["model"]
            if model not in by_model:
                by_model[model] = {"cost": 0.0, "requests": 0}
            by_model[model]["cost"] += float(row["estimated_cost_usd"])
            by_model[model]["requests"] += 1

        # Group by provider
        by_provider = {}
        for row in usage_data:
            provider = row["provider"]
            if provider not in by_provider:
                by_provider[provider] = {"cost": 0.0, "requests": 0}
            by_provider[provider]["cost"] += float(row["estimated_cost_usd"])
            by_provider[provider]["requests"] += 1

        # Daily cost trend (last 7 days)
        cost_trend = []
        for i in range(min(7, days)):
            day_start = end_date - timedelta(days=i + 1)
            day_end = end_date - timedelta(days=i)

            day_usage = [
                row
                for row in usage_data
                if day_start.isoformat() <= row["timestamp"] < day_end.isoformat()
            ]

            day_cost = sum(float(row["estimated_cost_usd"]) for row in day_usage)
            cost_trend.append(
                {
                    "date": day_start.strftime("%Y-%m-%d"),
                    "cost_usd": round(day_cost, 4),
                    "requests": len(day_usage),
                }
            )

        cost_trend.reverse()  # Chronological order

        return {
            "period_days": days,
            "total_cost_usd": round(total_cost, 4),
            "total_requests": total_requests,
            "daily_average_cost": round(daily_average, 4),
            "projected_monthly_cost": round(projected_monthly, 2),
            "average_cost_per_request": round(total_cost / total_requests, 6)
            if total_requests > 0
            else 0,
            "by_model": {
                k: {"cost_usd": round(v["cost"], 4), "requests": v["requests"]}
                for k, v in by_model.items()
            },
            "by_provider": {
                k: {"cost_usd": round(v["cost"], 4), "requests": v["requests"]}
                for k, v in by_provider.items()
            },
            "cost_trend": cost_trend,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Actual cost analysis failed: {str(e)}"
        )


@router.get("/budget/alert")
async def budget_alert(
    monthly_budget_usd: float = Query(
        ..., ge=0.01, description="Monthly budget in USD"
    ),
    days_to_check: int = Query(
        30, ge=1, le=90, description="Days to analyze for projection"
    ),
):
    """
    Budget alert system - check if current usage will exceed budget

    Analyzes recent usage to project monthly spending and alert if over budget.
    """

    try:
        # Get actual costs for projection
        actual_costs = await get_actual_costs(days_to_check)

        projected_monthly = actual_costs["projected_monthly_cost"]
        current_usage = actual_costs["total_cost_usd"]

        # Calculate budget status
        budget_utilization = (
            (projected_monthly / monthly_budget_usd) * 100
            if monthly_budget_usd > 0
            else 0
        )
        remaining_budget = monthly_budget_usd - projected_monthly

        # Determine alert level
        if budget_utilization >= 100:
            alert_level = "critical"
            message = f"BUDGET EXCEEDED: Projected monthly cost ${projected_monthly:.2f} exceeds budget ${monthly_budget_usd:.2f}"
        elif budget_utilization >= 80:
            alert_level = "warning"
            message = (
                f"Budget warning: Using {budget_utilization:.1f}% of monthly budget"
            )
        elif budget_utilization >= 60:
            alert_level = "caution"
            message = (
                f"Budget caution: Using {budget_utilization:.1f}% of monthly budget"
            )
        else:
            alert_level = "ok"
            message = f"Budget OK: Using {budget_utilization:.1f}% of monthly budget"

        return {
            "alert_level": alert_level,
            "message": message,
            "budget_status": {
                "monthly_budget_usd": monthly_budget_usd,
                "projected_monthly_cost": projected_monthly,
                "remaining_budget": round(remaining_budget, 2),
                "utilization_percent": round(budget_utilization, 1),
                "days_analyzed": days_to_check,
                "current_period_cost": current_usage,
            },
            "recommendations": {
                "switch_to_cheaper_model": projected_monthly > monthly_budget_usd,
                "reduce_usage": budget_utilization > 80,
                "increase_budget": projected_monthly > monthly_budget_usd * 1.2,
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Budget alert failed: {str(e)}")
