"""Security middleware and authentication for ClauseBot API.

Implements:
- Feature flag gating (FEATURE_CLAUSEBOT_PUBLIC)
- API key authentication for /v1/* endpoints
- IP allowlist enforcement
- Rate limiting with different tiers based on feature flag
- Request ID generation and structured logging
- Audit logging for security events
"""

import os
import uuid
import time
import logging
from typing import Optional, List
from datetime import datetime
from collections import defaultdict
from functools import wraps

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - request_id=%(request_id)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityConfig:
    """Central configuration for security features."""
    
    def __init__(self):
        # Feature flags
        self.feature_public = os.getenv("FEATURE_CLAUSEBOT_PUBLIC", "false").lower() == "true"
        
        # API authentication
        self.api_key_required = os.getenv("API_KEY_REQUIRED", "true").lower() == "true"
        api_keys_str = os.getenv("API_KEYS", "")
        self.api_keys = set(k.strip() for k in api_keys_str.split(",") if k.strip())
        
        # IP allowlist
        ip_allowlist_str = os.getenv("IP_ALLOWLIST", "")
        self.ip_allowlist = [ip.strip() for ip in ip_allowlist_str.split(",") if ip.strip()]
        
        # Rate limiting
        self.rate_limit_per_minute = int(os.getenv(
            "RATE_LIMIT_PUBLIC_PER_MINUTE" if self.feature_public else "RATE_LIMIT_PER_MINUTE",
            "60" if self.feature_public else "5"
        ))
        
        # SEO controls
        self.robots_noindex_preview = os.getenv("ROBOTS_NOINDEX_PREVIEW", "true").lower() == "true"
        self.robots_noindex_docs = os.getenv("ROBOTS_NOINDEX_DOCS", "true").lower() == "true"
        
        # Application metadata
        self.app_version = os.getenv("APP_VERSION", "unknown")
        self.app_name = os.getenv("APP_NAME", "clausebot-api")


config = SecurityConfig()


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for given identifier."""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > minute_ago
        ]
        
        # Check limit
        if len(self.requests[identifier]) >= self.requests_per_minute:
            return False
        
        # Record request
        self.requests[identifier].append(now)
        return True


rate_limiter = RateLimiter(config.rate_limit_per_minute)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware for ClauseBot API."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.config = config
        self.rate_limiter = rate_limiter
        self.audit_logger = logging.getLogger("audit")
    
    async def dispatch(self, request: Request, call_next):
        """Process each request through security layers."""
        # Generate and attach request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request ID to logging context
        extra = {"request_id": request_id}
        
        start_time = time.time()
        
        try:
            # Log incoming request
            logger.info(
                f"Incoming request: {request.method} {request.url.path}",
                extra={"request_id": request_id, "method": request.method, "path": request.url.path}
            )
            
            # Check if route is protected by feature flag
            if self._is_gated_route(request.url.path) and not self.config.feature_public:
                self._audit_log("blocked_gated_route", request, request_id)
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={"detail": "Service is not yet publicly available"},
                    headers={"X-Request-ID": request_id}
                )
            
            # Check IP allowlist (if configured)
            if self.config.ip_allowlist and self._is_protected_route(request.url.path):
                client_ip = self._get_client_ip(request)
                if not self._is_ip_allowed(client_ip):
                    self._audit_log("blocked_ip", request, request_id, {"ip": client_ip})
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "Access denied"},
                        headers={"X-Request-ID": request_id}
                    )
            
            # Check API key for protected routes
            if self.config.api_key_required and self._is_protected_route(request.url.path):
                if not self._validate_api_key(request):
                    self._audit_log("blocked_invalid_api_key", request, request_id)
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid or missing API key"},
                        headers={
                            "X-Request-ID": request_id,
                            "WWW-Authenticate": "Bearer"
                        }
                    )
            
            # Rate limiting
            identifier = self._get_rate_limit_identifier(request)
            if not self.rate_limiter.is_allowed(identifier):
                self._audit_log("rate_limited", request, request_id, {"identifier": identifier})
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded"},
                    headers={
                        "X-Request-ID": request_id,
                        "Retry-After": "60"
                    }
                )
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["X-App-Version"] = self.config.app_version
            
            # Add robots meta for preview/docs routes
            if self._should_noindex(request.url.path):
                response.headers["X-Robots-Tag"] = "noindex, nofollow"
            
            # Log response
            duration = time.time() - start_time
            logger.info(
                f"Request completed: {response.status_code} in {duration:.3f}s",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration": duration
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(
                f"Request error: {str(e)}",
                extra={"request_id": request_id, "error": str(e)},
                exc_info=True
            )
            self._audit_log("error", request, request_id, {"error": str(e)})
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"},
                headers={"X-Request-ID": request_id}
            )
    
    def _is_gated_route(self, path: str) -> bool:
        """Check if route requires FEATURE_CLAUSEBOT_PUBLIC flag."""
        # Gate all /v1/* API routes behind feature flag
        return path.startswith("/v1/")
    
    def _is_protected_route(self, path: str) -> bool:
        """Check if route requires API key authentication."""
        # Protect /v1/* API routes
        protected_prefixes = ["/v1/"]
        return any(path.startswith(prefix) for prefix in protected_prefixes)
    
    def _validate_api_key(self, request: Request) -> bool:
        """Validate API key from Authorization header or query param."""
        # Try Authorization header first (Bearer token)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if token in self.config.api_keys:
                return True
        
        # Try X-API-Key header
        api_key_header = request.headers.get("X-API-Key", "")
        if api_key_header in self.config.api_keys:
            return True
        
        # Try query parameter (less secure, only for development)
        api_key_query = request.query_params.get("api_key", "")
        if api_key_query in self.config.api_keys:
            return True
        
        return False
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        # Check for proxy headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_ip_allowed(self, ip: str) -> bool:
        """Check if IP is in allowlist."""
        if not self.config.ip_allowlist:
            return True
        
        # Simple exact match (could be enhanced with CIDR matching)
        for allowed_ip in self.config.ip_allowlist:
            if allowed_ip in ip or ip == allowed_ip:
                return True
        
        return False
    
    def _get_rate_limit_identifier(self, request: Request) -> str:
        """Get identifier for rate limiting."""
        # Use API key if present
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return f"key:{auth_header[7:]}"
        
        # Fall back to IP address
        return f"ip:{self._get_client_ip(request)}"
    
    def _should_noindex(self, path: str) -> bool:
        """Check if route should have noindex directive."""
        if self.config.robots_noindex_preview and "/preview" in path:
            return True
        if self.config.robots_noindex_docs and "/docs" in path:
            return True
        return False
    
    def _audit_log(self, event_type: str, request: Request, request_id: str, extra_data: dict = None):
        """Log security audit events."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "ip": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", "unknown"),
        }
        
        if extra_data:
            audit_entry.update(extra_data)
        
        self.audit_logger.warning(f"AUDIT: {event_type}", extra=audit_entry)


def get_request_id(request: Request) -> str:
    """Extract request ID from request state."""
    return getattr(request.state, "request_id", "unknown")


def require_feature_flag(feature_name: str):
    """Decorator to protect routes with feature flags."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if feature_name == "public" and not config.feature_public:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="This feature is not yet publicly available"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
