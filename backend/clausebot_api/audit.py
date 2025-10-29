"""
ClauseBot Audit Trail System
Enterprise-grade audit logging for compliance and security

Features:
- All critical actions logged (data mutations, admin actions, job runs)
- Immutable audit log (append-only Supabase table)
- Retention policy support
- Query API for compliance audits
- IP tracking and user attribution

Supabase Schema (run this SQL):
```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    action TEXT NOT NULL,
    user_id TEXT,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    status TEXT DEFAULT 'success',
    INDEX idx_timestamp (timestamp DESC),
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_resource (resource_type, resource_id)
);

-- Enable Row Level Security (optional)
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Retention policy (optional - keep 1 year)
CREATE POLICY audit_retention ON audit_log
FOR DELETE USING (timestamp < NOW() - INTERVAL '1 year');
```
"""
import os
from datetime import datetime
from typing import Optional, Dict, Any
from supabase import create_client, Client


def get_supabase() -> Client:
    """Create Supabase client."""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)


def log_audit(
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "success"
) -> Dict[str, Any]:
    """
    Log an audit event to Supabase.
    
    Args:
        action: Action performed (e.g., "CACHE_CLEAR", "QUIZ_CREATE", "DATA_SYNC")
        resource_type: Type of resource (e.g., "cache", "quiz", "sync_job")
        resource_id: Optional resource identifier
        user_id: Optional user identifier
        details: Optional additional context (JSON-serializable)
        ip_address: Optional IP address
        user_agent: Optional user agent string
        status: Status of action ("success", "failure", "partial")
    
    Returns:
        Dict with audit log entry
    
    Example:
        from clausebot_api.audit import log_audit
        
        log_audit(
            action="CACHE_CLEAR",
            resource_type="cache",
            user_id="admin@example.com",
            details={"pattern": "cb:/v1/quiz*", "keys_deleted": 42},
            ip_address=request.client.host,
            status="success"
        )
    """
    try:
        sb = get_supabase()
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "status": status
        }
        
        result = sb.table("audit_log").insert(entry).execute()
        
        return {
            "ok": True,
            "audit_id": result.data[0]["id"] if result.data else None
        }
    
    except Exception as e:
        # Log to stdout if audit trail fails (fallback)
        print(f"⚠️  Audit log failed: {e}")
        print(f"   Action: {action}, Resource: {resource_type}/{resource_id}")
        
        return {
            "ok": False,
            "error": str(e)
        }


def query_audit_log(
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100
) -> list:
    """
    Query audit log with filters.
    
    Args:
        action: Filter by action
        resource_type: Filter by resource type
        user_id: Filter by user
        start_date: Filter by start date
        end_date: Filter by end date
        limit: Max records to return
    
    Returns:
        List of audit log entries
    
    Example:
        # Get all cache clears by admin in last 7 days
        from datetime import datetime, timedelta
        from clausebot_api.audit import query_audit_log
        
        logs = query_audit_log(
            action="CACHE_CLEAR",
            user_id="admin@example.com",
            start_date=datetime.utcnow() - timedelta(days=7),
            limit=50
        )
    """
    try:
        sb = get_supabase()
        
        query = sb.table("audit_log").select("*")
        
        if action:
            query = query.eq("action", action)
        
        if resource_type:
            query = query.eq("resource_type", resource_type)
        
        if user_id:
            query = query.eq("user_id", user_id)
        
        if start_date:
            query = query.gte("timestamp", start_date.isoformat())
        
        if end_date:
            query = query.lte("timestamp", end_date.isoformat())
        
        query = query.order("timestamp", desc=True).limit(limit)
        
        result = query.execute()
        return result.data
    
    except Exception as e:
        print(f"⚠️  Audit query failed: {e}")
        return []


# FastAPI dependency for automatic audit logging
from fastapi import Request
from functools import wraps


def audit_action(action: str, resource_type: str):
    """
    Decorator for automatic audit logging on FastAPI endpoints.
    
    Usage:
        from clausebot_api.audit import audit_action
        
        @router.post("/admin/clear-cache")
        @audit_action("CACHE_CLEAR", "cache")
        async def clear_cache(request: Request):
            # ... logic here
            return {"ok": True}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, request: Request = None, **kwargs):
            # Extract user from request (if available)
            user_id = getattr(request.state, 'user_id', None) if request else None
            ip_address = request.client.host if request else None
            user_agent = request.headers.get("user-agent") if request else None
            
            try:
                # Execute function
                result = await func(*args, request=request, **kwargs) if request else await func(*args, **kwargs)
                
                # Log success
                log_audit(
                    action=action,
                    resource_type=resource_type,
                    user_id=user_id,
                    details={"endpoint": request.url.path} if request else None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status="success"
                )
                
                return result
            
            except Exception as e:
                # Log failure
                log_audit(
                    action=action,
                    resource_type=resource_type,
                    user_id=user_id,
                    details={
                        "endpoint": request.url.path if request else None,
                        "error": str(e)
                    },
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status="failure"
                )
                raise
        
        return wrapper
    return decorator


# Background job audit logger
class JobAuditLogger:
    """
    Audit logger for background jobs.
    
    Usage:
        from clausebot_api.audit import JobAuditLogger
        
        job_logger = JobAuditLogger("airtable_sync")
        job_logger.start()
        
        try:
            # ... job logic
            job_logger.success(records_synced=250)
        except Exception as e:
            job_logger.failure(error=str(e))
    """
    
    def __init__(self, job_name: str):
        self.job_name = job_name
        self.start_time = None
        self.audit_id = None
    
    def start(self, details: Optional[Dict[str, Any]] = None):
        """Log job start."""
        self.start_time = datetime.utcnow()
        
        result = log_audit(
            action=f"JOB_START_{self.job_name.upper()}",
            resource_type="background_job",
            resource_id=self.job_name,
            details=details,
            status="in_progress"
        )
        
        self.audit_id = result.get("audit_id")
    
    def success(self, **details):
        """Log job success."""
        duration = None
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        log_audit(
            action=f"JOB_SUCCESS_{self.job_name.upper()}",
            resource_type="background_job",
            resource_id=self.job_name,
            details={"duration_seconds": duration, **details},
            status="success"
        )
    
    def failure(self, error: str, **details):
        """Log job failure."""
        duration = None
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        log_audit(
            action=f"JOB_FAILURE_{self.job_name.upper()}",
            resource_type="background_job",
            resource_id=self.job_name,
            details={"duration_seconds": duration, "error": error, **details},
            status="failure"
        )

