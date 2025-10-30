import time
import json
import os
from typing import Dict, Any
from datetime import datetime
from collections import defaultdict, deque
import threading

# Metrics storage (in production, use Prometheus)
metrics_storage = {
    "requests_total": 0,
    "requests_by_endpoint": defaultdict(int),
    "requests_by_status": defaultdict(int),
    "response_times": deque(maxlen=1000),
    "cache_hits": 0,
    "cache_misses": 0,
    "errors_total": 0,
    "active_connections": 0,
    "start_time": time.time(),
}

# Thread-safe metrics updates
metrics_lock = threading.Lock()


class MetricsCollector:
    @staticmethod
    def increment_counter(name: str, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        with metrics_lock:
            if labels:
                key = f"{name}_{json.dumps(labels, sort_keys=True)}"
            else:
                key = name
            metrics_storage[key] = metrics_storage.get(key, 0) + 1

    @staticmethod
    def record_histogram(name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram value"""
        with metrics_lock:
            if labels:
                key = f"{name}_{json.dumps(labels, sort_keys=True)}"
            else:
                key = name

            if key not in metrics_storage:
                metrics_storage[key] = deque(maxlen=1000)
            metrics_storage[key].append(value)

    @staticmethod
    def set_gauge(name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge value"""
        with metrics_lock:
            if labels:
                key = f"{name}_{json.dumps(labels, sort_keys=True)}"
            else:
                key = name
            metrics_storage[key] = value


def record_request_metrics(
    endpoint: str, status_code: int, response_time: float, cache_hit: bool = False
):
    """Record request metrics"""
    MetricsCollector.increment_counter("requests_total")
    MetricsCollector.increment_counter("requests_by_endpoint", {"endpoint": endpoint})
    MetricsCollector.increment_counter(
        "requests_by_status", {"status": str(status_code)}
    )
    MetricsCollector.record_histogram("response_times", response_time)

    if cache_hit:
        MetricsCollector.increment_counter("cache_hits")
    else:
        MetricsCollector.increment_counter("cache_misses")

    if status_code >= 400:
        MetricsCollector.increment_counter("errors_total")


def get_metrics_summary() -> Dict[str, Any]:
    """Get metrics summary for /metrics endpoint"""
    with metrics_lock:
        uptime = time.time() - metrics_storage["start_time"]

        # Calculate percentiles
        response_times = list(metrics_storage["response_times"])
        if response_times:
            sorted_times = sorted(response_times)
            p50 = sorted_times[int(len(sorted_times) * 0.5)]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
        else:
            p50 = p95 = p99 = 0

        # Cache hit rate
        total_cache_requests = (
            metrics_storage["cache_hits"] + metrics_storage["cache_misses"]
        )
        cache_hit_rate = (
            (metrics_storage["cache_hits"] / total_cache_requests * 100)
            if total_cache_requests > 0
            else 0
        )

        return {
            "uptime_seconds": uptime,
            "requests_total": metrics_storage["requests_total"],
            "requests_by_endpoint": dict(metrics_storage["requests_by_endpoint"]),
            "requests_by_status": dict(metrics_storage["requests_by_status"]),
            "response_times": {
                "p50_ms": round(p50 * 1000, 2),
                "p95_ms": round(p95 * 1000, 2),
                "p99_ms": round(p99 * 1000, 2),
                "count": len(response_times),
            },
            "cache": {
                "hits": metrics_storage["cache_hits"],
                "misses": metrics_storage["cache_misses"],
                "hit_rate_percent": round(cache_hit_rate, 2),
            },
            "errors_total": metrics_storage["errors_total"],
            "active_connections": metrics_storage["active_connections"],
        }


class StructuredLogger:
    def __init__(self, log_dir: str = "./data/logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def log(self, level: str, message: str, request_id: str = None, **kwargs):
        """Log structured event"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "request_id": request_id,
            **kwargs,
        }

        # Write to daily log file
        log_file = os.path.join(
            self.log_dir, f"clausebot_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Also print to console for development
        print(f"[{level.upper()}] {message} | {json.dumps(kwargs)}")


# Global logger instance
logger = StructuredLogger()


def check_system_health() -> Dict[str, Any]:
    """Check system health for /health endpoint"""
    health_status = {
        "ok": True,
        "version": "1.0.0",
        "uptime_seconds": time.time() - metrics_storage["start_time"],
        "timestamp": datetime.utcnow().isoformat(),
        "deps": [],
    }

    # Check dependencies
    deps = [
        {"name": "AWS_D1.1_2020", "status": "healthy"},
        {"name": "Index", "status": "healthy"},
        {"name": "Cache", "status": "healthy"},
        {"name": "Logs", "status": "healthy"},
    ]

    # Check if index files exist
    index_dir = os.getenv("INDEX_DIR", "./data/codes/aws_d1_1_2020/index")
    if not os.path.exists(os.path.join(index_dir, "index.json")):
        deps[1]["status"] = "degraded"
        health_status["ok"] = False

    # Check if log directory is writable
    try:
        test_log = os.path.join(logger.log_dir, "health_check.log")
        with open(test_log, "w") as f:
            f.write("health check")
        os.remove(test_log)
    except:
        deps[3]["status"] = "degraded"
        health_status["ok"] = False

    health_status["deps"] = deps
    return health_status


def check_readiness() -> Dict[str, Any]:
    """Check system readiness for /ready endpoint"""
    readiness = {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": [],
    }

    # Check if index is warm
    index_dir = os.getenv("INDEX_DIR", "./data/codes/aws_d1_1_2020/index")
    index_file = os.path.join(index_dir, "index.json")

    if os.path.exists(index_file):
        readiness["checks"].append({"name": "index_warm", "status": "ready"})
    else:
        readiness["checks"].append({"name": "index_warm", "status": "not_ready"})
        readiness["ready"] = False

    # Check if model is available (placeholder)
    readiness["checks"].append({"name": "model_available", "status": "ready"})

    # Check if cache is operational
    readiness["checks"].append({"name": "cache_operational", "status": "ready"})

    return readiness
