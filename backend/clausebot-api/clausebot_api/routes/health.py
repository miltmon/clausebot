# Health and Diagnostics Router
from typing import Dict, Any
from fastapi import APIRouter
from collections import Counter
import os
from clausebot_api.airtable_data_source import (
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID, 
    AIRTABLE_TABLE,
    AIRTABLE_VIEW,
    _has_required_quiz_fields,
    _compute_status
)
from pyairtable import Table

router = APIRouter()

@router.get("/health/quiz/detailed")
def quiz_health_detailed() -> Dict[str, Any]:
    """Detailed quiz data health check with category and status breakdown"""
    
    if not (AIRTABLE_API_KEY and AIRTABLE_BASE_ID and AIRTABLE_TABLE):
        return {
            "error": "Airtable not configured",
            "configured": False
        }
    
    try:
        table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE)
        
        # Fetch up to 2000 records to analyze
        records = table.all(view=AIRTABLE_VIEW, max_records=2000)
        
        # Analyze records
        total_records = len(records)
        eligible_records = []
        status_distribution = Counter()
        category_distribution = Counter()
        
        for record in records:
            fields = record.get("fields", {})
            
            # Count by computed status
            computed_status = _compute_status(fields)
            status_distribution[computed_status] += 1
            
            # Check eligibility
            if _has_required_quiz_fields(fields):
                eligible_records.append(record)
                
                # Count by category for eligible records
                from clausebot_api.airtable_data_source import _first, CATEGORY_FIELDS
                category = _first(fields, CATEGORY_FIELDS) or "uncategorized"
                category_distribution[category] += 1
        
        exclude_needs_validation = os.getenv("EXCLUDE_NEEDS_VALIDATION", "1").lower() in ("1", "true", "yes")
        production_ready_statuses = ["verified", "production"]
        
        production_ready_count = sum(
            1 for r in eligible_records
            if _compute_status(r.get("fields", {})) in production_ready_statuses
        )
        
        return {
            "airtable": {
                "base_id": AIRTABLE_BASE_ID,
                "table": AIRTABLE_TABLE,
                "view": AIRTABLE_VIEW,
            },
            "records": {
                "total": total_records,
                "quiz_eligible": len(eligible_records),
                "production_ready": production_ready_count,
            },
            "filtering": {
                "exclude_needs_validation": exclude_needs_validation,
                "production_ready_statuses": production_ready_statuses,
            },
            "distribution": {
                "by_status": dict(status_distribution),
                "by_category": dict(category_distribution),
            },
            "env": {
                "EXCLUDE_NEEDS_VALIDATION": os.getenv("EXCLUDE_NEEDS_VALIDATION", "1"),
                "QUIZ_FILTER_FORMULA": os.getenv("QUIZ_FILTER_FORMULA", ""),
            }
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "configured": True,
            "connection_failed": True
        }

@router.get("/health/quiz/baseline")
def quiz_health_baseline() -> Dict[str, Any]:
    """Quick baseline check without detailed analysis"""
    
    if not (AIRTABLE_API_KEY and AIRTABLE_BASE_ID and AIRTABLE_TABLE):
        return {
            "status": "not_configured",
            "configured": False
        }
    
    try:
        table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE)
        
        # Quick check - just count first 100 records
        records = table.all(view=AIRTABLE_VIEW, max_records=100)
        
        eligible_count = sum(
            1 for r in records
            if _has_required_quiz_fields(r.get("fields", {}))
        )
        
        return {
            "status": "connected",
            "configured": True,
            "sample_size": len(records),
            "eligible_in_sample": eligible_count,
            "view": AIRTABLE_VIEW,
        }
        
    except Exception as e:
        return {
            "status": "error",
            "configured": True,
            "error": str(e)
        }

