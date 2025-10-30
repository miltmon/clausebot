#!/usr/bin/env python3
"""
Enhanced Exa.ai Webhook with HMAC Security
Production-ready webhook with signature verification and rate limiting
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import hmac
import time
from collections import defaultdict

# --- Enhanced Config ---
DRIVE_ROOT = os.getenv("DRIVE_ROOT", r"G:\ClauseBot_OPPS_Workspace")
INBOX_DIR = Path(DRIVE_ROOT) / "Shared" / "compliance_updates" / "inbox"
WEBHOOK_SECRET = os.getenv("EXA_WEBHOOK_SECRET", "dev-secret-change-in-prod")
MAX_ITEMS_PER_REQUEST = int(os.getenv("MAX_ITEMS_PER_REQUEST", "50"))
MAX_REQUEST_SIZE_MB = int(os.getenv("MAX_REQUEST_SIZE_MB", "10"))

# Rate limiting
rate_limiter = defaultdict(list)
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

INBOX_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="ClauseBot Pilot A – Exa Webset Ingest (Production)")
security = HTTPBearer()


class ExaItem(BaseModel):
    title: str = Field(..., description="Article/resource title", max_length=500)
    url: HttpUrl
    description: Optional[str] = Field(None, max_length=1000)
    detected_at: Optional[str] = Field(
        default=None, description="ISO8601, when this item was detected/updated"
    )
    sections: Optional[List[str]] = Field(None, max_items=20)
    impact_tags: Optional[List[str]] = Field(None, max_items=10)
    webset_id: Optional[str] = Field(None, max_length=100)
    change_id: Optional[str] = Field(None, max_length=200)


class IngestPayload(BaseModel):
    source: str = Field("exa.ai", regex="^exa\.ai$")
    webset_id: str = Field(..., max_length=100)
    items: List[ExaItem] = Field(..., max_items=MAX_ITEMS_PER_REQUEST)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def verify_webhook_signature(body: bytes, signature: str, secret: str) -> bool:
    """Verify HMAC-SHA256 signature from Exa.ai webhook"""
    if not signature.startswith("sha256="):
        return False

    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

    provided = signature[7:]  # Remove "sha256=" prefix
    return hmac.compare_digest(expected, provided)


def check_rate_limit(client_ip: str) -> bool:
    """Simple rate limiting by IP"""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    # Clean old entries
    rate_limiter[client_ip] = [
        req_time for req_time in rate_limiter[client_ip] if req_time > window_start
    ]

    # Check current count
    if len(rate_limiter[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False

    # Add current request
    rate_limiter[client_ip].append(now)
    return True


def sanitize_content(text: str) -> str:
    """Remove potential PII patterns from content"""
    import re

    # Remove email addresses
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL_REDACTED]", text
    )

    # Remove phone numbers
    text = re.sub(r"\b\d{3}-\d{3}-\d{4}\b", "[PHONE_REDACTED]", text)
    text = re.sub(r"\b\(\d{3}\)\s*\d{3}-\d{4}\b", "[PHONE_REDACTED]", text)

    # Remove potential SSNs
    text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_REDACTED]", text)

    return text


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Security middleware for request validation"""

    # Check request size
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Request too large")

    # Rate limiting
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    response = await call_next(request)
    return response


@app.get("/health")
def health():
    """Enhanced health check with security status"""
    return {
        "ok": True,
        "inbox": str(INBOX_DIR),
        "time": _now_iso(),
        "security": {
            "hmac_enabled": bool(
                WEBHOOK_SECRET and WEBHOOK_SECRET != "dev-secret-change-in-prod"
            ),
            "rate_limiting": True,
            "pii_sanitization": True,
        },
        "limits": {
            "max_items_per_request": MAX_ITEMS_PER_REQUEST,
            "max_request_size_mb": MAX_REQUEST_SIZE_MB,
            "rate_limit_per_hour": RATE_LIMIT_REQUESTS,
        },
    }


@app.post("/exa/webset/ingest")
async def ingest(request: Request):
    """
    Enhanced Exa.ai Webset Ingestion with Security
    - HMAC signature verification
    - Rate limiting
    - PII sanitization
    - Request size limits
    """

    # Get raw body for signature verification
    body = await request.body()

    # Verify HMAC signature (production requirement)
    signature = request.headers.get("X-Exa-Signature")
    if WEBHOOK_SECRET != "dev-secret-change-in-prod":  # Production mode
        if not signature:
            raise HTTPException(
                status_code=401, detail="Missing X-Exa-Signature header"
            )

        if not verify_webhook_signature(body, signature, WEBHOOK_SECRET):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # Parse payload
    try:
        payload_data = json.loads(body.decode("utf-8"))
        payload = IngestPayload(**payload_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")

    # Additional validation
    if payload.source != "exa.ai":
        raise HTTPException(status_code=400, detail="Unsupported source")

    if len(payload.items) == 0:
        raise HTTPException(status_code=400, detail="No items provided")

    written = []
    security_events = []

    for item in payload.items:
        # Normalize timestamps
        ts = item.detected_at or _now_iso()

        # Sanitize content for PII
        title = sanitize_content(item.title)
        description = sanitize_content(item.description or "")

        # Check for potential security issues
        if title != item.title or description != (item.description or ""):
            security_events.append(f"PII sanitized in item: {item.url}")

        # Provenance hashes (no full text)
        url_hash = _sha256(str(item.url))
        title_hash = _sha256(title.strip())

        doc = {
            "source": payload.source,
            "webset_id": payload.webset_id,
            "detected_at": ts,
            "artifact": {
                "title": title,
                "uri": str(item.url),
                "description": description[:600],  # Truncate long descriptions
                "sections": item.sections or [],
                "impact_tags": item.impact_tags or [],
            },
            "provenance": {
                "url_sha256": url_hash,
                "title_sha256": title_hash,
                "change_id": item.change_id or f"exa-{ts}-{url_hash[:8]}",
                "ingested_via": "webhook_hmac_verified"
                if signature
                else "webhook_dev_mode",
            },
            # CURSOR hint fields
            "impact_estimate": {"severity": None, "confidence": None},
            # Windsurf cascade metadata
            "windsurf_metadata": {
                "ingested_at": _now_iso(),
                "cascade_required": False,
                "hitl_required": False,
                "namespace": "test-ns",
            },
            # Security metadata
            "security": {
                "pii_sanitized": len(security_events) > 0,
                "signature_verified": bool(signature),
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent", "unknown")[:100],
            },
        }

        # Write one JSON per item (Drive-first)
        filename = f"exa_{payload.webset_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{url_hash[:10]}.json"
        file_path = INBOX_DIR / filename

        try:
            file_path.write_text(
                json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            written.append(filename)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to write file {filename}: {str(e)}"
            )

    # Log security events if any
    if security_events:
        security_log = {
            "timestamp": _now_iso(),
            "event_type": "pii_sanitization",
            "webset_id": payload.webset_id,
            "events": security_events,
            "client_ip": request.client.host,
        }

        security_log_path = INBOX_DIR.parent / "security_events.log"
        with open(security_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(security_log) + "\n")

    return {
        "accepted": len(written),
        "written": written,
        "inbox_path": str(INBOX_DIR),
        "security": {
            "signature_verified": bool(signature),
            "pii_events": len(security_events),
            "rate_limit_remaining": RATE_LIMIT_REQUESTS
            - len(rate_limiter[request.client.host]),
        },
    }


@app.get("/exa/inbox/status")
def inbox_status():
    """Enhanced inbox status with security metrics"""
    try:
        items = list(INBOX_DIR.glob("exa_*.json"))
        recent_items = sorted(items, key=lambda x: x.stat().st_mtime, reverse=True)[:10]

        # Security metrics
        security_log_path = INBOX_DIR.parent / "security_events.log"
        security_events_today = 0
        if security_log_path.exists():
            today = datetime.now().strftime("%Y-%m-%d")
            with open(security_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if today in line:
                        security_events_today += 1

        return {
            "inbox_path": str(INBOX_DIR),
            "total_items": len(items),
            "recent_items": [item.name for item in recent_items],
            "last_updated": _now_iso(),
            "security": {
                "events_today": security_events_today,
                "hmac_verification": WEBHOOK_SECRET != "dev-secret-change-in-prod",
                "rate_limiting_active": True,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inbox status error: {str(e)}")


@app.get("/exa/security/status")
def security_status():
    """Security status endpoint for monitoring"""
    return {
        "timestamp": _now_iso(),
        "security_features": {
            "hmac_verification": WEBHOOK_SECRET != "dev-secret-change-in-prod",
            "rate_limiting": True,
            "pii_sanitization": True,
            "request_size_limits": True,
            "signature_required": WEBHOOK_SECRET != "dev-secret-change-in-prod",
        },
        "current_limits": {
            "max_items_per_request": MAX_ITEMS_PER_REQUEST,
            "max_request_size_mb": MAX_REQUEST_SIZE_MB,
            "rate_limit_per_hour": RATE_LIMIT_REQUESTS,
        },
        "active_rate_limits": len(rate_limiter),
        "production_ready": WEBHOOK_SECRET != "dev-secret-change-in-prod",
    }


if __name__ == "__main__":
    import uvicorn

    # Production configuration
    config = {"host": "0.0.0.0", "port": 8088, "log_level": "info", "access_log": True}

    # Add SSL in production
    if os.getenv("SSL_CERT_PATH") and os.getenv("SSL_KEY_PATH"):
        config.update(
            {
                "ssl_certfile": os.getenv("SSL_CERT_PATH"),
                "ssl_keyfile": os.getenv("SSL_KEY_PATH"),
            }
        )

    print("🌊 Starting Enhanced Exa.ai Webhook Server")
    print(f"📁 Inbox: {INBOX_DIR}")
    print(
        f"🔐 HMAC Security: {'ENABLED' if WEBHOOK_SECRET != 'dev-secret-change-in-prod' else 'DEV MODE'}"
    )
    print(f"🚦 Rate Limiting: {RATE_LIMIT_REQUESTS} req/hour")

    uvicorn.run(app, **config)
