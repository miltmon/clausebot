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

# Field aliases (matches your Airtable)
STEM_FIELDS        = ("Question Text","Scenario","Question","Stem","Prompt")
CHOICE_A_FIELD     = "Option A"
CHOICE_B_FIELD     = "Option B"
CHOICE_C_FIELD     = "Option C"
CHOICE_D_FIELD     = "Option D"
CORRECT_FIELDS     = ("Correct Answer","Correct")
CATEGORY_FIELDS    = ("Reference Material","Question Category","Category")
CLAUSE_FIELDS      = ("Primary Code Reference","Clause","clause_ref")
EXPLANATION_FIELDS = ("Explanation of Correct Answer","Explanation")
ACTIVE_FIELDS      = ("Active","active")

def _first(fields: Dict[str, Any], names: tuple[str, ...]) -> Optional[Any]:
    for n in names:
        if n in fields and fields[n] not in (None, "", []):
            return fields[n]
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
        correct = correct[:1].upper()  # "C: ..." -> "C"

    item = {
        "id": rec.get("id", ""),
        "q": stem.strip(),
        "a": [str(x).strip() for x in choices],
        "correct": correct,
        "category": category,
        "clause_ref": clause,
        "explanation": expl,
        "source": "airtable",
    }

    # Strict completeness
    if not item["q"]: return None
    if any(not ch for ch in item["a"]): return None
    if item["correct"] not in ("A","B","C","D"): return None
    if not item["clause_ref"] or not item["explanation"]: return None
    return item

def _active_filter_formula(ui_category: str, at_category: str) -> str:
    # AND({Reference Material}='AWS D1.1', {Active}=1)
    field = CATEGORY_FIELDS[0]  # "Reference Material"
    return f"AND({{{field}}}='{at_category}', {{Active}}=1)"

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
                    sample = {"q": n["q"], "category": n["category"], "clause_ref": n["clause_ref"]}
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

def _translate_ui_category(ui_label: str) -> str:
    try:
        from clausebot_api.category_map import at_category_for
        return at_category_for(ui_label)
    except Exception:
        return ui_label

def _fetch_airtable_items(ui_category: str, limit: int) -> List[Dict[str, Any]]:
    if not (AIRTABLE_API_KEY and AIRTABLE_BASE_ID and AIRTABLE_TABLE):
        raise HTTPException(503, "Airtable unavailable (env)")
    at_category = _translate_ui_category(ui_category)
    try:
        tbl = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE)
        formula = _active_filter_formula(ui_category, at_category)
        recs = tbl.all(view=AIRTABLE_VIEW, formula=formula, max_records=max(1, min(limit, 200)))
        items: List[Dict[str, Any]] = []
        for r in recs:
            n = _normalize(r)
            if n:
                items.append(n)
        return items
    except Exception as e:
        logger.error("Airtable fetch failed: %s", e)
        raise HTTPException(503, "Airtable fetch error")

def get_questions(ui_category: str, count: int = 10) -> List[Dict[str, Any]]:
    if not test_airtable_connection():
        raise HTTPException(503, "Airtable unavailable (check PAT/base/table/view)")
    items = _fetch_airtable_items(ui_category, limit=max(count * 5, 50))
    if len(items) < count:
        raise HTTPException(422, f"Not enough active questions in '{ui_category}' (have {len(items)}, need {count}).")
    return items[:count]
