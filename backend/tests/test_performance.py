"""
ClauseBot Performance Tests
Ensures response times meet SLA targets

Targets:
- Cached responses: <50ms (p95)
- Uncached responses: <1000ms (p95)
- Cache hit rate: >70%
- Database queries: <200ms (p95)

Run with:
    pytest tests/test_performance.py -v
    pytest tests/test_performance.py -v --benchmark-only
"""
import pytest
import time
import asyncio
from typing import List
from fastapi.testclient import TestClient


# Mark all tests in this file as performance tests
pytestmark = pytest.mark.performance


@pytest.fixture
def api_client():
    """Create FastAPI test client."""
    from clausebot_api.main import app
    return TestClient(app)


@pytest.fixture
def cache():
    """Get cache instance."""
    from clausebot_api.cache import cache
    return cache


class TestAPIPerformance:
    """API endpoint performance tests."""
    
    def test_health_endpoint_latency(self, api_client):
        """Health endpoint should respond in <20ms."""
        # Warm up
        api_client.get("/health")
        
        # Measure 10 requests
        latencies: List[float] = []
        for _ in range(10):
            start = time.time()
            response = api_client.get("/health")
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)
            
            assert response.status_code == 200
        
        # Check p95 latency
        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)]
        
        assert p95 < 20, f"Health endpoint p95={p95:.2f}ms (target <20ms)"
        print(f"✅ Health endpoint p95: {p95:.2f}ms")
    
    def test_quiz_cached_latency(self, api_client):
        """Cached quiz responses should be <50ms (p95)."""
        # Prime cache
        api_client.get("/quiz?count=5")
        
        # Measure cached requests
        latencies: List[float] = []
        for _ in range(20):
            start = time.time()
            response = api_client.get("/quiz?count=5")
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)
            
            assert response.status_code == 200
        
        # Check p95 latency
        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)]
        
        assert p95 < 50, f"Quiz cached p95={p95:.2f}ms (target <50ms)"
        print(f"✅ Quiz cached p95: {p95:.2f}ms")
    
    def test_quiz_uncached_latency(self, api_client, cache):
        """Uncached quiz responses should be <1000ms (p95)."""
        # Clear cache
        asyncio.run(cache.delete_pattern("cb:/v1/quiz*"))
        
        # Measure uncached requests (different params each time)
        latencies: List[float] = []
        for i in range(10):
            start = time.time()
            response = api_client.get(f"/quiz?count={i+1}")
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)
            
            assert response.status_code == 200
        
        # Check p95 latency
        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)]
        
        assert p95 < 1000, f"Quiz uncached p95={p95:.2f}ms (target <1000ms)"
        print(f"✅ Quiz uncached p95: {p95:.2f}ms")
    
    def test_cache_health_latency(self, api_client):
        """Cache health endpoint should respond in <30ms."""
        # Warm up
        api_client.get("/health/cache")
        
        # Measure requests
        latencies: List[float] = []
        for _ in range(10):
            start = time.time()
            response = api_client.get("/health/cache")
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)
            
            assert response.status_code == 200
        
        # Check p95 latency
        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)]
        
        assert p95 < 30, f"Cache health p95={p95:.2f}ms (target <30ms)"
        print(f"✅ Cache health p95: {p95:.2f}ms")


class TestCachePerformance:
    """Cache system performance tests."""
    
    @pytest.mark.asyncio
    async def test_cache_hit_rate(self, cache):
        """Cache hit rate should be >70% in production usage patterns."""
        # Simulate production usage (80% repeated queries, 20% unique)
        repeated_key = "test_repeated"
        hits = 0
        misses = 0
        
        # Prime cache
        await cache.set(repeated_key, {"test": "data"})
        
        for i in range(100):
            if i < 80:
                # 80% repeated queries (cache hits)
                result = await cache.get(repeated_key)
                if result:
                    hits += 1
                else:
                    misses += 1
            else:
                # 20% unique queries (cache misses)
                result = await cache.get(f"test_unique_{i}")
                if result:
                    hits += 1
                else:
                    misses += 1
        
        hit_rate = (hits / (hits + misses)) * 100
        
        # In this test, we expect ~80% hit rate
        assert hit_rate >= 75, f"Cache hit rate {hit_rate:.1f}% below target (>75%)"
        print(f"✅ Cache hit rate: {hit_rate:.1f}%")
    
    @pytest.mark.asyncio
    async def test_cache_get_latency(self, cache):
        """Cache GET operations should be <5ms (p95)."""
        key = "perf_test_key"
        data = {"test": "data" * 100}  # ~1KB
        
        # Prime cache
        await cache.set(key, data)
        
        # Measure GET latency
        latencies: List[float] = []
        for _ in range(100):
            start = time.time()
            await cache.get(key)
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)
        
        # Check p95
        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)]
        
        assert p95 < 5, f"Cache GET p95={p95:.2f}ms (target <5ms)"
        print(f"✅ Cache GET p95: {p95:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_cache_set_latency(self, cache):
        """Cache SET operations should be <10ms (p95)."""
        data = {"test": "data" * 100}  # ~1KB
        
        # Measure SET latency
        latencies: List[float] = []
        for i in range(100):
            start = time.time()
            await cache.set(f"perf_test_{i}", data)
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)
        
        # Check p95
        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)]
        
        assert p95 < 10, f"Cache SET p95={p95:.2f}ms (target <10ms)"
        print(f"✅ Cache SET p95: {p95:.2f}ms")


class TestDatabasePerformance:
    """Database query performance tests."""
    
    @pytest.mark.asyncio
    async def test_supabase_query_latency(self):
        """Supabase queries should complete in <200ms (p95)."""
        from supabase import create_client
        import os
        
        sb = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_KEY"]
        )
        
        # Measure query latency
        latencies: List[float] = []
        for _ in range(10):
            start = time.time()
            result = sb.table("quiz_items").select("*").limit(10).execute()
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)
            
            assert len(result.data) > 0
        
        # Check p95
        latencies.sort()
        p95 = latencies[int(len(latencies) * 0.95)]
        
        assert p95 < 200, f"Supabase query p95={p95:.2f}ms (target <200ms)"
        print(f"✅ Supabase query p95: {p95:.2f}ms")


class TestEndToEndPerformance:
    """End-to-end performance scenarios."""
    
    def test_quiz_workflow_e2e(self, api_client):
        """Complete quiz workflow should complete in <2s."""
        start = time.time()
        
        # 1. Fetch quiz
        quiz_response = api_client.get("/quiz?count=10")
        assert quiz_response.status_code == 200
        
        # 2. Check health
        health_response = api_client.get("/health")
        assert health_response.status_code == 200
        
        # 3. Check cache health
        cache_response = api_client.get("/health/cache")
        assert cache_response.status_code == 200
        
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 2000, f"E2E workflow took {elapsed_ms:.2f}ms (target <2000ms)"
        print(f"✅ E2E workflow: {elapsed_ms:.2f}ms")


# Benchmark tests (optional, requires pytest-benchmark)
def test_cache_benchmark(benchmark, cache):
    """Benchmark cache operations."""
    import asyncio
    
    def cache_operation():
        loop = asyncio.get_event_loop()
        loop.run_until_complete(cache.get_or_set(
            "benchmark_key",
            lambda: {"test": "data"}
        ))
    
    result = benchmark(cache_operation)
    print(f"✅ Cache benchmark: {result}")


# Performance regression tests
class TestPerformanceRegressions:
    """Detect performance regressions against baseline."""
    
    BASELINE_HEALTH_MS = 20
    BASELINE_QUIZ_CACHED_MS = 50
    BASELINE_QUIZ_UNCACHED_MS = 1000
    
    def test_no_health_regression(self, api_client):
        """Ensure health endpoint hasn't regressed."""
        api_client.get("/health")  # Warm up
        
        start = time.time()
        response = api_client.get("/health")
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < self.BASELINE_HEALTH_MS * 1.5, \
            f"Health regression: {elapsed_ms:.2f}ms > baseline {self.BASELINE_HEALTH_MS}ms * 1.5"
        
        print(f"✅ No health regression: {elapsed_ms:.2f}ms")
    
    def test_no_quiz_regression(self, api_client):
        """Ensure quiz endpoint hasn't regressed."""
        # Prime cache
        api_client.get("/quiz?count=5")
        
        start = time.time()
        response = api_client.get("/quiz?count=5")
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < self.BASELINE_QUIZ_CACHED_MS * 1.5, \
            f"Quiz regression: {elapsed_ms:.2f}ms > baseline {self.BASELINE_QUIZ_CACHED_MS}ms * 1.5"
        
        print(f"✅ No quiz regression: {elapsed_ms:.2f}ms")

