#!/usr/bin/env python3
"""
ClauseBot Pilot A - Exa.ai Webset Webhook Integration
Push-style integration for real-time standards monitoring
"""

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

# --- config ---
DRIVE_ROOT = r"G:\ClauseBot_OPPS_Workspace"
INBOX_DIR = Path(DRIVE_ROOT) / "Shared" / "compliance_updates" / "inbox"
INBOX_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="ClauseBot Pilot A – Exa Webset Ingest")


class ExaItem(BaseModel):
    title: str = Field(..., description="Article/resource title")
    url: HttpUrl
    description: Optional[str] = None
    detected_at: Optional[str] = Field(
        default=None, description="ISO8601, when this item was detected/updated"
    )
    sections: Optional[List[str]] = None  # e.g., ["6.1.4","6.2.1"]
    impact_tags: Optional[List[str]] = None  # e.g., ["procedure","preheat"]
    webset_id: Optional[str] = None  # e.g., "aws_cwi_resources"
    change_id: Optional[str] = None  # stable id if Exa provides one


class IngestPayload(BaseModel):
    source: str = "exa.ai"
    webset_id: str
    items: List[ExaItem]


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@app.get("/health")
def health():
    return {"ok": True, "inbox": str(INBOX_DIR), "time": _now_iso()}


@app.post("/exa/webset/ingest")
async def ingest(payload: IngestPayload, request: Request):
    """
    Windsurf Exa.ai Webset Ingestion Endpoint
    Receives metadata-only items and writes to Drive inbox for CURSOR processing
    """
    # Basic guardrail
    if payload.source != "exa.ai":
        raise HTTPException(status_code=400, detail="Unsupported source")

    written = []
    for item in payload.items:
        # Normalize timestamps
        ts = item.detected_at or _now_iso()

        # Provenance hashes (no full text)
        url_hash = _sha256(str(item.url))
        title_hash = _sha256(item.title.strip())

        doc = {
            "source": payload.source,
            "webset_id": payload.webset_id,
            "detected_at": ts,
            "artifact": {
                "title": item.title,
                "uri": str(item.url),
                "description": (item.description or "")[:600],  # trim long desc
                "sections": item.sections or [],
                "impact_tags": item.impact_tags or [],
            },
            "provenance": {
                "url_sha256": url_hash,
                "title_sha256": title_hash,
                "change_id": item.change_id or f"exa-{ts}-{url_hash[:8]}",
            },
            # CURSOR hint fields (can be empty—CURSOR will score later)
            "impact_estimate": {"severity": None, "confidence": None},
            # Windsurf cascade metadata
            "windsurf_metadata": {
                "ingested_at": _now_iso(),
                "cascade_required": False,  # CURSOR will determine
                "hitl_required": False,  # Based on impact scoring
                "namespace": "test-ns",  # Default cascade target
            },
        }

        # Write one JSON per item (Drive-first)
        filename = f"exa_{payload.webset_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{url_hash[:10]}.json"
        (INBOX_DIR / filename).write_text(
            json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        written.append(filename)

    return {"accepted": len(written), "written": written, "inbox_path": str(INBOX_DIR)}


@app.get("/exa/inbox/status")
def inbox_status():
    """Check inbox status and recent items"""
    try:
        items = list(INBOX_DIR.glob("exa_*.json"))
        recent_items = sorted(items, key=lambda x: x.stat().st_mtime, reverse=True)[:10]

        return {
            "inbox_path": str(INBOX_DIR),
            "total_items": len(items),
            "recent_items": [item.name for item in recent_items],
            "last_updated": _now_iso(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inbox status error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8088)
