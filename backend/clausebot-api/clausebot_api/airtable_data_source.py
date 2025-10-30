# Strict Airtable adapter: no fallbacks, 503/422 on failure
from __future__ import annotations
from typing import List, Dict, Any, Optional
import os, logging
from fastapi import HTTPException
from pyairtable import Table

logger = logging.getLogger(__name__)

# Env contract
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY") or os.getenv("AIRTABLE_PAT")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID") or os.getenv("AIRTABLE_V2_BASE_ID")
AIRTABLE_TABLE   = os.getenv("AIRTABLE_TABLE") or os.getenv("AIRTABLE_V2_QUESTIONS_TABLE") or "Questions"
AIRTABLE_VIEW    = os.getenv("AIRTABLE_VIEW") or os.getenv("AIRTABLE_V2_QUESTIONS_VIEW") or "Grid view"
CATEGORY_FIELD   = os.getenv("AIRTABLE_CATEGORY_FIELD", "Question Category")
STATUS_OK        = os.getenv("AIRTABLE_STATUS_OK", "Verified")

# Field aliases (matches your actual Airtable schema)
STEM_FIELDS        = ("Scenario","Specific Challenge","Question Text","Question","Stem","Prompt")
CHOICE_A_FIELD     = "Answer Choice A"
CHOICE_B_FIELD     = "Answer Choice B"
CHOICE_C_FIELD     = "Answer Choice C"
CHOICE_D_FIELD     = "Answer Choice D"
CORRECT_FIELDS     = ("Correct Answer","Correct")
CATEGORY_FIELDS    = ("Question Category","BOK Category","Category Name","Category")
CLAUSE_FIELDS      = ("Primary Code Reference","Clause","clause_ref")
EXPLANATION_FIELDS = ("Explanation of Correct Answer","Explanation")
ACTIVE_FIELDS      = ("Status","status")

def _first(fields: Dict[str, Any], names: tuple[str, ...]) -> Optional[Any]:
    for n in names:
        val = fields.get(n)
        if val not in (None, "", []):
            # If Airtable returns a list (multi-select), take first item
            if isinstance(val, list):
                return val[0] if val else None
            return val
    return None

def _normalize(rec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    f = rec.get("fields", {})
    stem = _first(f, STEM_FIELDS) or ""
    choices = [
        f.get(CHOICE_A_FIELD, "") or "",
        f.get(CHOICE_B_FIELD, "") or "",
        f.get(CHOICE_C_FIELD, "") or "",
        f.get(CHOICE_D_FIELD, "") or "",
    ]
    correct  = (_first(f, CORRECT_FIELDS) or "").strip()
    category = (_first(f, CATEGORY_FIELDS) or "").strip()
    clause   = (_first(f, CLAUSE_FIELDS) or "").strip()
    expl     = (_first(f, EXPLANATION_FIELDS) or "").strip()

    if isinstance(correct, str):
        # Handle formats like "B: Vertical position groove weld" -> "B"
        correct = correct.strip()
        if ":" in correct:
            correct = correct.split(":")[0].strip()
        correct = correct[:1].upper()  # Extract first letter and uppercase

    item = {
        "id": rec.get("id", ""),
        "question": stem.strip(),
        "options": [str(x).strip() for x in choices],
        "correct_answer": correct,
        "category": category,
        "clause_ref": clause,
        "explanation": expl,
        "source": "airtable",
    }

    # Strict completeness
    if not item["question"]: return None
    if any(not ch for ch in item["options"]): return None
    if item["correct_answer"] not in ("A","B","C","D"): return None
    if not item["clause_ref"] or not item["explanation"]: return None
    return item

def _compute_status(fields: dict) -> str:
    """Compute status from emojis and text across all fields"""
    blob = " | ".join(str(v) for v in fields.values() if v is not None).lower()
    if "✅" in blob or "verified" in blob:
        return "verified"
    if "⚠" in blob or "needs validation" in blob or "todo" in blob or "draft" in blob:
        return "needs_validation"
    return "unknown"

def _has_required_quiz_fields(fields: dict) -> bool:
    """Check if record has minimum required fields for quiz"""
    # Check for question text (Scenario or Specific Challenge)
    question = _first(fields, STEM_FIELDS)
    if not question or not question.strip():
        return False
    
    # Check for answer choices (all 4 must be present and non-empty)
    choices = [
        fields.get(CHOICE_A_FIELD, "").strip(),
        fields.get(CHOICE_B_FIELD, "").strip(), 
        fields.get(CHOICE_C_FIELD, "").strip(),
        fields.get(CHOICE_D_FIELD, "").strip()
    ]
    # Skip records with validation indicators in choices
    for choice in choices:
        if not choice or "⚠️" in choice or "needs validation" in choice.lower():
            return False
        
    # Check for correct answer
    correct = _first(fields, CORRECT_FIELDS)
    if not correct or not correct.strip():
        return False
        
    return True

def _build_filter_formula(category: str) -> str:
    """Build Airtable filter formula with optional category match"""
    # Use env var for optional filtering
    formula = os.getenv("QUIZ_FILTER_FORMULA", "").strip()
    if formula:
        return formula
        
    # No filtering by default - let code handle eligibility
    if not category or not category.strip():
        return ""
    
    # Filter by category only if specified
    safe_category = category.strip().replace("'", "''")
    return f"LOWER(TRIM({{{CATEGORY_FIELD}}}))=LOWER('{safe_category}')"

def test_airtable_connection() -> bool:
    if not (AIRTABLE_API_KEY and AIRTABLE_BASE_ID and AIRTABLE_TABLE):
        logger.warning("Airtable env missing")
        return False
    try:
        Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE).first()
        return True
    except Exception as e:
        logger.error("Airtable connection test failed: %s", e)
        return False

def get_airtable_health() -> Dict[str, Any]:
    ok = test_airtable_connection()
    sample = None
    if ok:
        try:
            tbl = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE)
            r = tbl.first(view=AIRTABLE_VIEW)
            if r:
                n = _normalize(r)
                if n:
                    sample = {"question": n["question"], "category": n["category"], "clause_ref": n["clause_ref"]}
        except Exception as e:
            logger.error("Health sample failed: %s", e)
            ok = False
    return {
        "service": "airtable",
        "status": "connected" if ok else "disconnected",
        "configured": bool(AIRTABLE_API_KEY and AIRTABLE_BASE_ID and AIRTABLE_TABLE),
        "base_id": AIRTABLE_BASE_ID,
        "table": AIRTABLE_TABLE,
        "view": AIRTABLE_VIEW,
        "sample": sample,
    }

def get_questions(category: str, count: int) -> List[Dict[str, Any]]:
    """Fetch quiz questions from Airtable with computed status filtering"""
    if not (AIRTABLE_API_KEY and AIRTABLE_BASE_ID and AIRTABLE_TABLE):
        raise HTTPException(status_code=503, detail="Airtable not configured")
    
    try:
        table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE)
        
        # Fetch records without category filtering (filter in code instead)
        # This allows us to serve questions even if category field is missing/uncategorized
        formula = os.getenv("QUIZ_FILTER_FORMULA", "").strip()
        params = {"view": AIRTABLE_VIEW, "max_records": min(count * 10, 500)}
        if formula:
            params["formula"] = formula
            
        records = table.all(**params)
        
        # Filter by required fields, computed status, and optionally category
        eligible_records = []
        enable_category_filter = os.getenv("ENABLE_CATEGORY_FILTER", "0").lower() in ("1", "true", "yes")
        
        for record in records:
            fields = record.get("fields", {})
            
            # Check if has required quiz fields
            if not _has_required_quiz_fields(fields):
                continue
                
            # Compute status and optionally exclude "needs validation"
            computed_status = _compute_status(fields)
            exclude_needs_validation = os.getenv("EXCLUDE_NEEDS_VALIDATION", "1").lower() in ("1", "true", "yes")
            
            if exclude_needs_validation and computed_status == "needs_validation":
                continue
            
            # Optional category filtering (disabled by default since most questions are uncategorized)
            if enable_category_filter and category:
                record_category = _first(fields, CATEGORY_FIELDS) or ""
                # Convert to string in case Airtable returns a list
                record_category = str(record_category) if record_category else ""
                if record_category.lower().strip() != category.lower().strip():
                    continue
                
            # Transform record
            item = _normalize(record)
            if item:
                item["computed_status"] = computed_status
                eligible_records.append(item)
                
                if len(eligible_records) >= count:
                    break
        
        if not eligible_records:
            raise HTTPException(
                status_code=422, 
                detail=f"No eligible quiz questions found (requested {count}, found 0 after filtering). Category filter: {'enabled' if enable_category_filter else 'disabled'}"
            )
        
        return eligible_records
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Airtable fetch error: {str(e)}"
        )
