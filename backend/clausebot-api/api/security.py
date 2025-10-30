import time
from typing import Dict, Optional
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import json

# API Key management
API_KEYS = {
    "mobile_app": {
        "key": "cb_mobile_2025_secure_key_12345",
        "scopes": ["read:clause", "gen:script", "write:log"],
        "rate_limit": 100,  # requests per minute
        "description": "AWS CWI Mobile App",
    },
    "lms_system": {
        "key": "cb_lms_2025_secure_key_67890",
        "scopes": ["read:clause", "gen:script", "write:log"],
        "rate_limit": 200,  # requests per minute
        "description": "Learning Management System",
    },
    "admin": {
        "key": "cb_admin_2025_secure_key_admin",
        "scopes": [
            "read:clause",
            "gen:script",
            "write:log",
            "admin:cache",
            "admin:index",
        ],
        "rate_limit": 500,  # requests per minute
        "description": "Administrative Access",
    },
}

# Rate limiting storage (in production, use Redis)
rate_limit_storage: Dict[str, Dict[str, int]] = {}

# CORS allowlist
ALLOWED_ORIGINS = [
    "https://www.miltmonndt.com",
    "https://clausebot.miltmonndt.com",  # Production ClauseBot UI
    "https://miltmon-80193.bubbleapps.io",
    "capacitor://localhost",  # Mobile app
    "http://localhost:3000",  # Local development
    "http://localhost:5173",  # Local development
    "http://localhost:4173",  # Preview server
    "http://localhost:8081",  # ClauseBot web interface
]


class APIKeyAuth(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(APIKeyAuth, self).__init__(auto_error=auto_error)

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        credentials = await super(APIKeyAuth, self).__call__(request)
        if credentials:
            if not self.verify_api_key(credentials.credentials):
                raise HTTPException(status_code=401, detail="Invalid API key")
            return credentials
        else:
            raise HTTPException(status_code=401, detail="API key required")

    def verify_api_key(self, api_key: str) -> bool:
        return api_key in [key_data["key"] for key_data in API_KEYS.values()]


def get_api_key_info(api_key: str) -> Optional[Dict]:
    for key_id, key_data in API_KEYS.items():
        if key_data["key"] == api_key:
            return {"id": key_id, **key_data}
    return None


def check_rate_limit(api_key: str, request_id: str) -> bool:
    """Check if request is within rate limit"""
    key_info = get_api_key_info(api_key)
    if not key_info:
        return False

    current_time = int(time.time() / 60)  # Current minute
    rate_key = f"{api_key}:{current_time}"

    if rate_key not in rate_limit_storage:
        rate_limit_storage[rate_key] = {"count": 0, "requests": []}

    if rate_limit_storage[rate_key]["count"] >= key_info["rate_limit"]:
        return False

    rate_limit_storage[rate_key]["count"] += 1
    rate_limit_storage[rate_key]["requests"].append(request_id)

    # Clean up old entries (keep last 5 minutes)
    old_keys = [
        k for k in rate_limit_storage.keys() if int(k.split(":")[-1]) < current_time - 5
    ]
    for old_key in old_keys:
        del rate_limit_storage[old_key]

    return True


def check_scope(api_key: str, required_scope: str) -> bool:
    """Check if API key has required scope"""
    key_info = get_api_key_info(api_key)
    if not key_info:
        return False
    return required_scope in key_info["scopes"]


def generate_request_id() -> str:
    """Generate unique request ID for tracking"""
    return f"req_{int(time.time() * 1000)}_{secrets.token_hex(4)}"


def log_security_event(
    event_type: str, api_key: str, request_id: str, details: Dict = None
):
    """Log security events for audit trail"""
    key_info = get_api_key_info(api_key)
    log_entry = {
        "timestamp": time.time(),
        "event_type": event_type,
        "request_id": request_id,
        "api_key_id": key_info["id"] if key_info else "unknown",
        "details": details or {},
    }

    # In production, send to structured logging system
    print(f"SECURITY_LOG: {json.dumps(log_entry)}")


def validate_cors_origin(origin: str) -> bool:
    """Validate CORS origin"""
    return origin in ALLOWED_ORIGINS


# Security middleware
async def security_middleware(request: Request, call_next):
    """Security middleware for all requests"""
    request_id = generate_request_id()
    request.state.request_id = request_id

    # CORS validation
    origin = request.headers.get("origin")
    if origin and not validate_cors_origin(origin):
        log_security_event("cors_violation", "none", request_id, {"origin": origin})
        raise HTTPException(status_code=403, detail="Origin not allowed")

    # API key validation for protected endpoints
    if request.url.path.startswith("/v1/"):
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            log_security_event("missing_auth", "none", request_id)
            raise HTTPException(status_code=401, detail="API key required")

        api_key = auth_header[7:]  # Remove "Bearer " prefix
        # Use the global function instead of self method
        valid_key = False
        for key_data in API_KEYS.values():
            if key_data["key"] == api_key:
                valid_key = True
                break

        if not valid_key:
            log_security_event("invalid_auth", api_key, request_id)
            raise HTTPException(status_code=401, detail="Invalid API key")

        # Rate limiting
        if not check_rate_limit(api_key, request_id):
            log_security_event("rate_limit_exceeded", api_key, request_id)
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        request.state.api_key = api_key

    response = await call_next(request)

    # Add security headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response
