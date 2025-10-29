"""
ClauseBot Task Queue Service
Enqueue background jobs from API endpoints

Usage:
    from clausebot_api.services.queue import task_queue
    
    # Enqueue a reindex job
    job = task_queue.enqueue_reindex("4.1.2")
    
    # Check job status
    status = task_queue.get_job_status(job.id)
"""
import os
from typing import Optional
from redis import Redis
from rq import Queue
from rq.job import Job


class TaskQueue:
    """Wrapper for RQ task queue."""
    
    def __init__(self):
        kv_url = os.getenv("KV_URL")
        
        if not kv_url:
            print("⚠️  KV_URL not set - task queue disabled")
            self.redis = None
            self.default_queue = None
            self.slow_queue = None
        else:
            self.redis = Redis.from_url(kv_url)
            self.default_queue = Queue("default", connection=self.redis)
            self.slow_queue = Queue("slow", connection=self.redis)
    
    def is_enabled(self) -> bool:
        """Check if task queue is configured."""
        return self.redis is not None
    
    def enqueue_reindex(self, clause: Optional[str] = None) -> Optional[Job]:
        """
        Enqueue a reindex job.
        
        Args:
            clause: Optional specific clause to reindex
        
        Returns:
            RQ Job instance or None if queue disabled
        """
        if not self.is_enabled():
            print("⚠️  Task queue disabled - skipping reindex job")
            return None
        
        from jobs.tasks import reindex_payload
        return self.slow_queue.enqueue(reindex_payload, clause)
    
    def enqueue_export(
        self,
        edition: str = "AWS D1.1:2025",
        format: str = "csv"
    ) -> Optional[Job]:
        """Enqueue a quiz results export job."""
        if not self.is_enabled():
            return None
        
        from jobs.tasks import export_quiz_results
        return self.default_queue.enqueue(export_quiz_results, edition, format)
    
    def enqueue_analytics(self, period: str = "daily") -> Optional[Job]:
        """Enqueue an analytics report generation job."""
        if not self.is_enabled():
            return None
        
        from jobs.tasks import generate_analytics_report
        return self.default_queue.enqueue(generate_analytics_report, period)
    
    def enqueue_cache_warm(self, clause_num: str) -> Optional[Job]:
        """Enqueue a cache warming job for a specific clause."""
        if not self.is_enabled():
            return None
        
        from jobs.tasks import warm_cache_for_clause
        return self.default_queue.enqueue(warm_cache_for_clause, clause_num)
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """
        Get status of a job by ID.
        
        Returns:
            Dict with job status or None if not found
        """
        if not self.is_enabled():
            return None
        
        try:
            job = Job.fetch(job_id, connection=self.redis)
            return {
                "id": job.id,
                "status": job.get_status(),
                "result": job.result,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "ended_at": job.ended_at.isoformat() if job.ended_at else None,
            }
        except Exception as e:
            return {"error": str(e)}


# Global task queue instance
task_queue = TaskQueue()

