"""
Wrapped Quiz Route - Structured logging with correlation IDs
"""

import uuid
import logging
import traceback
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("quiz")

router = APIRouter()


class QuizSpec(BaseModel):
    count: int = 10
    difficulty: Optional[str] = None
    standard: Optional[str] = None
    mode: Optional[str] = None


@router.get("/v1/quiz")
def quiz_get(
    count: int = Query(10, ge=1, le=50, description="Number of questions"),
    difficulty: Optional[str] = Query(None, description="Difficulty level"),
    category: Optional[str] = Query(None, description="Question category"),
):
    """
    GET endpoint for quiz generation with correlation ID tracking
    """
    cid = str(uuid.uuid4())[:8]

    try:
        log.info(
            f"quiz_get cid={cid} count={count} difficulty={difficulty} category={category}"
        )

        # Import here to avoid circular imports
        from airtable_data_source import get_quiz_source

        # Get questions from data source
        all_questions = get_quiz_source()
        log.info(f"quiz_get cid={cid} loaded_questions={len(all_questions)}")

        if not all_questions:
            log.warning(f"quiz_get cid={cid} no_questions_available")
            return {
                "error": "no_questions",
                "cid": cid,
                "message": "No questions available from data source",
            }

        # Filter and limit questions
        filtered_questions = all_questions
        if category:
            filtered_questions = [
                q
                for q in filtered_questions
                if q.get("category", "").lower() == category.lower()
            ]

        # Take requested count
        selected_questions = filtered_questions[:count]

        log.info(f"quiz_get cid={cid} returning_questions={len(selected_questions)}")

        return {
            "questions": selected_questions,
            "count": len(selected_questions),
            "total_available": len(all_questions),
            "cid": cid,
        }

    except Exception as e:
        error_msg = str(e)
        stack_trace = traceback.format_exc()

        log.error(f"quiz_get cid={cid} error={error_msg}")
        log.error(f"quiz_get cid={cid} stack_trace:\n{stack_trace}")

        # Return structured error without leaking sensitive info
        return {
            "error": "internal_error",
            "cid": cid,
            "message": "Quiz generation failed - check logs for details",
        }


@router.post("/v1/quiz")
def quiz_post(spec: Optional[Dict[str, Any]] = None):
    """
    POST endpoint - accepts both styles while stabilizing schemas
    """
    cid = str(uuid.uuid4())[:8]

    try:
        # Parse spec with defaults
        if spec is None:
            spec = {}

        count = int(spec.get("count", 10) or 10)
        difficulty = spec.get("difficulty")
        category = spec.get("category")

        log.info(f"quiz_post cid={cid} delegating to GET with count={count}")

        # Delegate to GET endpoint
        return quiz_get(count=count, difficulty=difficulty, category=category)

    except Exception as e:
        error_msg = str(e)
        stack_trace = traceback.format_exc()

        log.error(f"quiz_post cid={cid} error={error_msg}")
        log.error(f"quiz_post cid={cid} stack_trace:\n{stack_trace}")

        return {
            "error": "internal_error",
            "cid": cid,
            "message": "Quiz generation failed - check logs for details",
        }
