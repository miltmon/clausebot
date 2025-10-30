"""
Airtable Sample Probe - Bypasses quiz logic, tests data normalization
"""

from fastapi import APIRouter
import os
from pyairtable import Table

router = APIRouter()


@router.get("/v1/airtable/sample")
def airtable_sample():
    """
    Returns 1 normalized item from Airtable to test data flow
    Bypasses all quiz generation logic
    """
    token = os.getenv("AIRTABLE_TOKEN")
    base = os.getenv("AIRTABLE_BASE_ID")
    table_id = os.getenv("AIRTABLE_TABLE_ID") or os.getenv("AIRTABLE_TABLE_NAME")
    view = os.getenv("AIRTABLE_VIEW_ID")

    if not (token and base and table_id):
        return {
            "ok": False,
            "error": "missing_config",
            "note": "Airtable credentials not configured",
        }

    try:
        # Connect to Airtable
        table = Table(token, base, table_id)
        kwargs = {"page_size": 1}
        if view:
            kwargs["view"] = view

        # Get first record
        records = list(table.iterate(**kwargs))

        if not records:
            return {
                "ok": True,
                "items": [],
                "note": "No rows visible in view/table",
                "config": {"base_id": base, "table_id": table_id, "view_id": view},
            }

        # Normalize first record
        record = records[0]
        fields = record.get("fields", {})

        # Extract common quiz fields (defensive)
        normalized = {
            "record_id": record.get("id"),
            "question": fields.get("Question", ""),
            "answer_a": fields.get("Answer Choice A", ""),
            "answer_b": fields.get("Answer Choice B", ""),
            "answer_c": fields.get("Answer Choice C", ""),
            "answer_d": fields.get("Answer Choice D", ""),
            "correct": fields.get("Correct Answer", ""),
            "clause": fields.get("Primary Code Reference", ""),
            "category": fields.get("Question Category", ""),
            "explanation": fields.get("Explanation of Correct Answer", ""),
            "raw_fields": list(fields.keys()),  # Show available fields
        }

        return {
            "ok": True,
            "items": [normalized],
            "total_records": len(records),
            "config": {"base_id": base, "table_id": table_id, "view_id": view},
        }

    except Exception as e:
        return {
            "ok": False,
            "error": "airtable_error",
            "message": str(e)[:200],
            "config": {"base_id": base, "table_id": table_id, "view_id": view},
        }
