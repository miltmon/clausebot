"""
ClauseBot Model Router - Provider-Agnostic LLM Interface
Supports OpenAI, Anthropic, Google Gemini, and Ollama
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import httpx
from pydantic import BaseModel

# Configuration
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")  # openai|anthropic|google|ollama
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Cost estimation per 1K tokens (approximate, as of 2024)
COST_PER_1K_TOKENS = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "gemini-pro": {"input": 0.0005, "output": 0.0015},
    "gemini-pro-vision": {"input": 0.0025, "output": 0.01},
    "ollama": {"input": 0.0, "output": 0.0},  # Local models are free
}


class ModelUsage(BaseModel):
    """Track model usage for cost monitoring"""

    timestamp: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    endpoint: Optional[str] = None


class ModelResponse(BaseModel):
    """Standardized response from any model provider"""

    content: str
    usage: ModelUsage
    provider: str
    model: str
    finish_reason: Optional[str] = None


async def log_usage_to_supabase(usage: ModelUsage):
    """Log model usage to Supabase for cost tracking"""
    try:
        from supabase import create_client

        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not SUPABASE_URL or not SUPABASE_KEY:
            print("⚠️ Supabase credentials not configured for usage logging")
            return

        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Create model_usage table if it doesn't exist (run this SQL once)
        # CREATE TABLE model_usage (
        #     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        #     timestamp TIMESTAMPTZ NOT NULL,
        #     provider TEXT NOT NULL,
        #     model TEXT NOT NULL,
        #     input_tokens INTEGER NOT NULL,
        #     output_tokens INTEGER NOT NULL,
        #     estimated_cost_usd DECIMAL(10,6) NOT NULL,
        #     request_id TEXT,
        #     user_id TEXT,
        #     endpoint TEXT,
        #     created_at TIMESTAMPTZ DEFAULT NOW()
        # );

        result = (
            supabase.table("model_usage")
            .insert(
                {
                    "timestamp": usage.timestamp,
                    "provider": usage.provider,
                    "model": usage.model,
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                    "estimated_cost_usd": usage.estimated_cost_usd,
                    "request_id": usage.request_id,
                    "user_id": usage.user_id,
                    "endpoint": usage.endpoint,
                }
            )
            .execute()
        )

        print(
            f"📊 Usage logged: {usage.provider}/{usage.model} - ${usage.estimated_cost_usd:.4f}"
        )

    except Exception as e:
        print(f"⚠️ Failed to log usage to Supabase: {e}")


def estimate_cost(provider_model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost for a model request"""
    costs = COST_PER_1K_TOKENS.get(provider_model, {"input": 0.01, "output": 0.03})

    input_cost = (input_tokens / 1000) * costs["input"]
    output_cost = (output_tokens / 1000) * costs["output"]

    return round(input_cost + output_cost, 6)


async def llm_chat_openai(
    messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000
) -> ModelResponse:
    """OpenAI API integration"""

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not configured")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        response.raise_for_status()
        data = response.json()

    # Extract usage and content
    content = data["choices"][0]["message"]["content"]
    usage_data = data["usage"]

    usage = ModelUsage(
        timestamp=datetime.now(timezone.utc).isoformat(),
        provider="openai",
        model=MODEL_NAME,
        input_tokens=usage_data["prompt_tokens"],
        output_tokens=usage_data["completion_tokens"],
        estimated_cost_usd=estimate_cost(
            MODEL_NAME, usage_data["prompt_tokens"], usage_data["completion_tokens"]
        ),
    )

    # Log usage asynchronously
    asyncio.create_task(log_usage_to_supabase(usage))

    return ModelResponse(
        content=content,
        usage=usage,
        provider="openai",
        model=MODEL_NAME,
        finish_reason=data["choices"][0].get("finish_reason"),
    )


async def llm_chat_anthropic(
    messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000
) -> ModelResponse:
    """Anthropic Claude API integration"""

    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not configured")

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }

    # Convert OpenAI format to Anthropic format
    system_message = ""
    anthropic_messages = []

    for msg in messages:
        if msg["role"] == "system":
            system_message = msg["content"]
        else:
            anthropic_messages.append(msg)

    payload = {
        "model": MODEL_NAME,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": anthropic_messages,
    }

    if system_message:
        payload["system"] = system_message

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages", headers=headers, json=payload
        )
        response.raise_for_status()
        data = response.json()

    content = data["content"][0]["text"]
    usage_data = data["usage"]

    usage = ModelUsage(
        timestamp=datetime.now(timezone.utc).isoformat(),
        provider="anthropic",
        model=MODEL_NAME,
        input_tokens=usage_data["input_tokens"],
        output_tokens=usage_data["output_tokens"],
        estimated_cost_usd=estimate_cost(
            MODEL_NAME, usage_data["input_tokens"], usage_data["output_tokens"]
        ),
    )

    asyncio.create_task(log_usage_to_supabase(usage))

    return ModelResponse(
        content=content,
        usage=usage,
        provider="anthropic",
        model=MODEL_NAME,
        finish_reason=data.get("stop_reason"),
    )


async def llm_chat_google(
    messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000
) -> ModelResponse:
    """Google Gemini API integration"""

    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not configured")

    # Convert to Gemini format
    gemini_messages = []
    for msg in messages:
        role = "user" if msg["role"] in ["user", "system"] else "model"
        gemini_messages.append({"role": role, "parts": [{"text": msg["content"]}]})

    payload = {
        "contents": gemini_messages,
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GOOGLE_API_KEY}"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    content = data["candidates"][0]["content"]["parts"][0]["text"]

    # Estimate tokens (Gemini doesn't always return usage)
    input_tokens = (
        sum(len(msg["content"].split()) for msg in messages) * 1.3
    )  # Rough estimate
    output_tokens = len(content.split()) * 1.3

    usage = ModelUsage(
        timestamp=datetime.now(timezone.utc).isoformat(),
        provider="google",
        model=MODEL_NAME,
        input_tokens=int(input_tokens),
        output_tokens=int(output_tokens),
        estimated_cost_usd=estimate_cost(
            MODEL_NAME, int(input_tokens), int(output_tokens)
        ),
    )

    asyncio.create_task(log_usage_to_supabase(usage))

    return ModelResponse(
        content=content,
        usage=usage,
        provider="google",
        model=MODEL_NAME,
        finish_reason=data["candidates"][0].get("finishReason"),
    )


async def llm_chat_ollama(
    messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000
) -> ModelResponse:
    """Ollama local model integration"""

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "options": {"temperature": temperature, "num_predict": max_tokens},
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(f"{OLLAMA_HOST}/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()

    content = data["message"]["content"]

    # Estimate tokens for local models
    input_tokens = sum(len(msg["content"].split()) for msg in messages) * 1.3
    output_tokens = len(content.split()) * 1.3

    usage = ModelUsage(
        timestamp=datetime.now(timezone.utc).isoformat(),
        provider="ollama",
        model=MODEL_NAME,
        input_tokens=int(input_tokens),
        output_tokens=int(output_tokens),
        estimated_cost_usd=0.0,  # Local models are free
    )

    asyncio.create_task(log_usage_to_supabase(usage))

    return ModelResponse(
        content=content,
        usage=usage,
        provider="ollama",
        model=MODEL_NAME,
        finish_reason="stop",
    )


async def llm_chat(
    messages: List[Dict],
    temperature: float = 0.7,
    max_tokens: int = 1000,
    user_id: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> ModelResponse:
    """
    Universal LLM chat interface - routes to configured provider
    """

    try:
        if MODEL_PROVIDER == "openai":
            response = await llm_chat_openai(messages, temperature, max_tokens)
        elif MODEL_PROVIDER == "anthropic":
            response = await llm_chat_anthropic(messages, temperature, max_tokens)
        elif MODEL_PROVIDER == "google":
            response = await llm_chat_google(messages, temperature, max_tokens)
        elif MODEL_PROVIDER == "ollama":
            response = await llm_chat_ollama(messages, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported model provider: {MODEL_PROVIDER}")

        # Add tracking metadata
        response.usage.user_id = user_id
        response.usage.endpoint = endpoint

        return response

    except Exception as e:
        print(f"❌ LLM chat error ({MODEL_PROVIDER}/{MODEL_NAME}): {e}")
        raise


def get_available_providers() -> Dict[str, Any]:
    """Get available providers and their configuration status"""
    return {
        "current_provider": MODEL_PROVIDER,
        "current_model": MODEL_NAME,
        "providers": {
            "openai": {
                "configured": bool(OPENAI_API_KEY),
                "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            },
            "anthropic": {
                "configured": bool(ANTHROPIC_API_KEY),
                "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            },
            "google": {
                "configured": bool(GOOGLE_API_KEY),
                "models": ["gemini-pro", "gemini-pro-vision"],
            },
            "ollama": {
                "configured": True,  # Assume local Ollama is available
                "models": ["llama2", "codellama", "mistral", "neural-chat"],
            },
        },
    }


def estimate_monthly_cost(
    provider_model: str,
    monthly_calls: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
) -> float:
    """Estimate monthly cost for a given usage pattern"""
    cost_per_call = estimate_cost(provider_model, avg_input_tokens, avg_output_tokens)
    return round(cost_per_call * monthly_calls, 2)
