"""
Quiz API Routes for ClauseBot
Provides quiz questions from Airtable data source
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import random
import logging
from airtable_data_source import get_quiz_source, test_airtable_connection

logger = logging.getLogger(__name__)

router = APIRouter()


class QuizChoice(BaseModel):
    key: str = Field(..., description="Choice key (A, B, C, D)")
    text: str = Field(..., description="Choice text")


class QuizQuestion(BaseModel):
    id: str = Field(..., description="Unique question ID")
    question: str = Field(..., description="Question text")
    choices: List[QuizChoice] = Field(..., description="Answer choices")
    correct: str = Field(..., description="Correct answer key")
    clause: str = Field(..., description="AWS D1.1 clause reference")
    category: str = Field(..., description="Question category")
    explanation: Optional[str] = Field(
        None, description="Explanation of correct answer"
    )
    source: str = Field(..., description="Data source (airtable or fallback)")


class QuizResponse(BaseModel):
    questions: List[QuizQuestion] = Field(..., description="Quiz questions")
    total_available: int = Field(..., description="Total questions available")
    source_status: str = Field(..., description="Data source status")


class QuizHealthResponse(BaseModel):
    status: str = Field(..., description="Connection status")
    message: str = Field(..., description="Status message")
    questions_count: int = Field(..., description="Number of questions available")
    fallback: bool = Field(..., description="Whether using fallback data")


@router.get("/v1/quiz", response_model=QuizResponse)
async def get_quiz(
    count: int = Query(5, ge=1, le=20, description="Number of questions to return"),
    category: Optional[str] = Query(None, description="Filter by question category"),
    shuffle: bool = Query(True, description="Shuffle the questions"),
):
    """
    Get quiz questions from Airtable data source

    - **count**: Number of questions to return (1-20)
    - **category**: Optional category filter
    - **shuffle**: Whether to randomize question order
    """
    try:
        # Get all questions from data source
        all_questions = get_quiz_source()

        if not all_questions:
            raise HTTPException(
                status_code=503,
                detail="No quiz questions available - check data source configuration",
            )

        # Filter by category if specified
        if category:
            filtered_questions = [
                q
                for q in all_questions
                if q.get("category", "").lower() == category.lower()
            ]
            if not filtered_questions:
                raise HTTPException(
                    status_code=404,
                    detail=f"No questions found for category: {category}",
                )
            questions_pool = filtered_questions
        else:
            questions_pool = all_questions

        # Shuffle if requested
        if shuffle:
            random.shuffle(questions_pool)

        # Select requested number of questions
        selected_questions = questions_pool[:count]

        # Convert to response format
        quiz_questions = []
        for q in selected_questions:
            # Convert choices to proper format
            choices = []
            choice_keys = ["A", "B", "C", "D"]
            for i, choice_text in enumerate(q.get("choices", [])):
                if choice_text.strip():  # Only include non-empty choices
                    choices.append(
                        QuizChoice(key=choice_keys[i], text=choice_text.strip())
                    )

            quiz_questions.append(
                QuizQuestion(
                    id=q.get("id", f"q-{random.randint(1000, 9999)}"),
                    question=q.get("question", ""),
                    choices=choices,
                    correct=q.get("correct", "A"),
                    clause=q.get("clause", ""),
                    category=q.get("category", "General"),
                    explanation=q.get("explanation"),
                    source=q.get("source", "unknown"),
                )
            )

        # Determine source status
        source_status = (
            "airtable"
            if any(q.source == "airtable" for q in quiz_questions)
            else "fallback"
        )

        return QuizResponse(
            questions=quiz_questions,
            total_available=len(all_questions),
            source_status=source_status,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate quiz: {str(e)}"
        )


@router.get("/v1/quiz/health", response_model=QuizHealthResponse)
async def quiz_health():
    """
    Check the health of the quiz data source (Airtable connection)
    """
    try:
        health_status = test_airtable_connection()

        return QuizHealthResponse(
            status=health_status["status"],
            message=health_status["message"],
            questions_count=health_status.get("questions_count", 0),
            fallback=health_status["fallback"],
        )

    except Exception as e:
        logger.error(f"Error checking quiz health: {e}")
        return QuizHealthResponse(
            status="error",
            message=f"Health check failed: {str(e)}",
            questions_count=0,
            fallback=True,
        )


@router.get("/v1/quiz/categories")
async def get_quiz_categories():
    """
    Get available question categories
    """
    try:
        all_questions = get_quiz_source()
        categories = list(
            set(
                q.get("category", "General") for q in all_questions if q.get("category")
            )
        )
        categories.sort()

        return {"categories": categories, "total_questions": len(all_questions)}

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get categories: {str(e)}"
        )
