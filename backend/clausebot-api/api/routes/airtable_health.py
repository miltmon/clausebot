"""
Airtable Health Probe - Zero-risk connectivity validation
"""

from fastapi import APIRouter
from pyairtable import Table
import os

router = APIRouter()


@router.get("/health/airtable")
def health_airtable():
    """
    Green/red probe for Airtable credentials and base access
    Returns specific error codes for precise diagnosis
    """
    token = os.getenv("AIRTABLE_TOKEN")
    base = os.getenv("AIRTABLE_BASE_ID")
    table = os.getenv("AIRTABLE_TABLE_ID") or os.getenv("AIRTABLE_TABLE_NAME")
    view = os.getenv("AIRTABLE_VIEW_ID")

    # Check environment variables
    if not (token and base and table):
        return {
            "ok": False,
            "error": "missing_env",
            "details": {
                "token": bool(token),
                "base": bool(base),
                "table": bool(table),
                "view": bool(view),
            },
        }

    try:
        # Attempt minimal connection test
        t = Table(token, base, table)
        kwargs = {"page_size": 1}
        if view:
            kwargs["view"] = view

        # Try to pull a single record
        peek = next(iter(t.iterate(**kwargs)), None)

        return {
            "ok": True,
            "has_record": bool(peek),
            "config": {
                "base_id": base,
                "table_id": table,
                "view_id": view,
                "token_prefix": token[:8] + "..." if token else None,
            },
        }

    except Exception as e:
        msg = str(e).lower()

        # Map common errors to specific codes
        if "401" in msg or "unauthorized" in msg:
            code = "401_unauthorized"
        elif "403" in msg or "forbidden" in msg:
            code = "403_forbidden"
        elif "404" in msg or "not found" in msg:
            code = "404_not_found"
        elif "422" in msg or "unprocessable" in msg:
            code = "422_invalid_request"
        else:
            code = "unknown_error"

        return {
            "ok": False,
            "error": code,
            "message": str(e)[:200],  # Truncate to avoid leaking sensitive info
        }
