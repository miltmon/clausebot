"""
ClauseBot Background Worker
Processes async jobs via RQ (Redis Queue) + Valkey

Queues:
    - default: Standard priority tasks (analytics, exports)
    - slow: Long-running tasks (reindexing, bulk updates)

Usage:
    python -m jobs.worker
"""
import os
import sys
from redis import Redis
from rq import Worker, Queue, Connection


def main():
    """Start the RQ worker listening on configured queues."""
    print("🚀 ClauseBot Background Worker")
    print("="*60)
    
    # Get Redis connection
    kv_url = os.environ.get("KV_URL")
    if not kv_url:
        print("❌ ERROR: KV_URL not set")
        sys.exit(1)
    
    print(f"📡 Connecting to: {kv_url[:30]}...")
    redis_conn = Redis.from_url(kv_url)
    
    # Test connection
    try:
        redis_conn.ping()
        print("✅ Connected to Valkey/Redis")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)
    
    # Define queues to listen on
    listen = ["default", "slow"]
    print(f"👂 Listening on queues: {', '.join(listen)}")
    
    # Start worker
    print("="*60)
    print("⚡ Worker ready - waiting for jobs...")
    print("   Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    with Connection(redis_conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()


if __name__ == "__main__":
    main()

