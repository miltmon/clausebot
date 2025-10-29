"""
ClauseBot Cache Layer - Valkey/Redis-compatible caching
Provides sub-50ms lookups for hot paths (quiz, references, code indices)

Usage:
    from clausebot_api.cache import cache
    
    data = await cache.get_or_set(
        "my-key",
        producer=lambda: expensive_operation()
    )
"""
import os
import json
import hashlib
import asyncio
from typing import Callable, Any, Optional
from redis.asyncio import Redis


def _key_for(path: str, payload: Optional[dict] = None) -> str:
    """
    Generate a stable cache key from a path and payload.
    
    Args:
        path: API path or cache namespace (e.g., "/v1/quiz")
        payload: Optional dict of parameters to hash
    
    Returns:
        Cache key like "cb:/v1/quiz:a1b2c3d4"
    """
    if payload:
        h = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()[:16]
        return f"cb:{path}:{h}"
    return f"cb:{path}"


class KVCache:
    """
    Async cache wrapper for Valkey/Redis.
    
    Features:
    - Automatic JSON serialization
    - Configurable TTL via QUIZ_CACHE_TTL env var
    - get_or_set pattern for easy integration
    - Namespace prefix ("cb:") for safe key management
    """
    
    def __init__(self):
        self.ttl = int(os.getenv("QUIZ_CACHE_TTL", "300"))  # 5 min default
        kv_url = os.getenv("KV_URL")
        
        if not kv_url:
            # Graceful fallback if cache not configured
            print("⚠️  KV_URL not set - cache disabled (all calls will be cache misses)")
            self.redis = None
        else:
            self.redis = Redis.from_url(kv_url, decode_responses=True)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache, return None if missing or cache disabled."""
        if not self.redis:
            return None
        
        try:
            val = await self.redis.get(key)
            if val is not None:
                return json.loads(val)
        except Exception as e:
            print(f"⚠️  Cache GET error for {key}: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache with optional TTL override."""
        if not self.redis:
            return False
        
        try:
            await self.redis.set(
                key,
                json.dumps(value),
                ex=ttl or self.ttl
            )
            return True
        except Exception as e:
            print(f"⚠️  Cache SET error for {key}: {e}")
            return False
    
    async def get_or_set(
        self,
        key: str,
        producer: Callable,
        ttl: Optional[int] = None
    ) -> Any:
        """
        Get from cache, or compute and cache the result.
        
        Args:
            key: Cache key
            producer: Async or sync callable that produces the value on cache miss
            ttl: Optional TTL override (seconds)
        
        Returns:
            Cached or freshly computed value
        
        Example:
            async def fetch_quiz():
                return {"questions": [...]}
            
            data = await cache.get_or_set("quiz:d1.1", fetch_quiz)
        """
        # Try cache first
        val = await self.get(key)
        if val is not None:
            return val
        
        # Cache miss - produce value
        if asyncio.iscoroutinefunction(producer):
            data = await producer()
        else:
            data = producer()
        
        # Store in cache
        await self.set(key, data, ttl)
        
        return data
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"⚠️  Cache DELETE error for {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Redis pattern (e.g., "cb:/v1/quiz*")
        
        Returns:
            Number of keys deleted
        """
        if not self.redis:
            return 0
        
        try:
            count = 0
            async for key in self.redis.scan_iter(match=pattern):
                await self.redis.delete(key)
                count += 1
            return count
        except Exception as e:
            print(f"⚠️  Cache DELETE_PATTERN error for {pattern}: {e}")
            return 0
    
    async def health_check(self) -> dict:
        """Check cache connectivity and return stats."""
        if not self.redis:
            return {
                "ok": False,
                "message": "Cache not configured",
                "enabled": False
            }
        
        try:
            await self.redis.ping()
            info = await self.redis.info("stats")
            return {
                "ok": True,
                "enabled": True,
                "ttl_seconds": self.ttl,
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            return {
                "ok": False,
                "enabled": True,
                "error": str(e)
            }


# Global cache instance
cache = KVCache()


# Convenience function for generating keys
def cache_key(path: str, **params) -> str:
    """
    Generate a cache key for a given path and parameters.
    
    Example:
        key = cache_key("/v1/quiz", clause="4.1", count=10)
        # Returns: "cb:/v1/quiz:a1b2c3d4e5f6"
    """
    return _key_for(path, params if params else None)

