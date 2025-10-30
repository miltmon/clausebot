"""
Quiz API Router for ClauseBot
Provides quiz questions with fallback data when Airtable is not available
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import random
import logging

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


def get_fallback_quiz_data() -> List[Dict[str, Any]]:
    """Fallback quiz data when Airtable is not available"""
    return [
        {
            "id": "aws-d1.1-undercut-1",
            "question": "According to AWS D1.1, what is the maximum allowable undercut depth for statically loaded members?",
            "choices": {
                "A": "1/32 inch (0.8 mm)",
                "B": "1/16 inch (1.6 mm)",
                "C": "3/32 inch (2.4 mm)",
                "D": "1/8 inch (3.2 mm)",
            },
            "correct": "A",
            "clause": "AWS D1.1 Clause 6.9.1",
            "category": "Visual Inspection",
            "explanation": "For statically loaded members, undercut shall not exceed 1/32 inch (0.8 mm) in depth according to AWS D1.1 Clause 6.9.1.",
            "source": "fallback",
        },
        {
            "id": "aws-d1.1-joint-prep-1",
            "question": "What is the primary purpose of joint preparation in welding according to AWS D1.1?",
            "choices": {
                "A": "To improve appearance",
                "B": "To ensure proper penetration and fusion",
                "C": "To reduce welding time",
                "D": "To minimize material usage",
            },
            "correct": "B",
            "clause": "AWS D1.1 Clause 2.3",
            "category": "Joint Preparation",
            "explanation": "Joint preparation ensures proper penetration and fusion, which is critical for weld quality and structural integrity.",
            "source": "fallback",
        },
        {
            "id": "aws-d1.1-preheat-1",
            "question": "What is the minimum preheat temperature for welding ASTM A514 steel with thickness greater than 2.5 inches?",
            "choices": {
                "A": "200°F (93°C)",
                "B": "300°F (149°C)",
                "C": "400°F (204°C)",
                "D": "500°F (260°C)",
            },
            "correct": "C",
            "clause": "AWS D1.1 Clause 3.3.2",
            "category": "Preheat",
            "explanation": "AWS D1.1 requires 400°F minimum preheat for A514 steel over 2.5 inches thick.",
            "source": "fallback",
        },
        {
            "id": "aws-d1.1-wps-1",
            "question": "Which of the following is NOT a required variable in a Welding Procedure Specification (WPS)?",
            "choices": {
                "A": "Base metal specification",
                "B": "Welding process",
                "C": "Welder certification number",
                "D": "Joint design",
            },
            "correct": "C",
            "clause": "AWS D1.1 Clause 4.1",
            "category": "WPS/PQR",
            "explanation": "Welder certification number is not part of the WPS; it is tracked separately for qualification records.",
            "source": "fallback",
        },
        {
            "id": "aws-d1.1-inspection-1",
            "question": "What is the minimum qualification requirement for a Certified Welding Inspector (CWI)?",
            "choices": {
                "A": "2 years welding experience",
                "B": "5 years welding-related experience",
                "C": "Engineering degree",
                "D": "AWS certification only",
            },
            "correct": "B",
            "clause": "AWS D1.1 Clause 6.1",
            "category": "Inspection",
            "explanation": "AWS requires a minimum of 5 years of welding-related experience for CWI qualification.",
            "source": "fallback",
        },
    ]


@router.get("/v1/quiz", response_model=QuizResponse)
async def get_quiz(
    count: int = Query(5, ge=1, le=20, description="Number of questions to return"),
    category: Optional[str] = Query(None, description="Filter by question category"),
    shuffle: bool = Query(True, description="Shuffle the questions"),
):
    """
    Get quiz questions from fallback data

    - **count**: Number of questions to return (1-20)
    - **category**: Optional category filter
    - **shuffle**: Whether to randomize question order
    """
    try:
        # Get fallback questions
        all_questions = get_fallback_quiz_data()

        if not all_questions:
            raise HTTPException(status_code=503, detail="No quiz questions available")

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
            for key, text in q.get("choices", {}).items():
                if text.strip():  # Only include non-empty choices
                    choices.append(QuizChoice(key=key, text=text.strip()))

            quiz_questions.append(
                QuizQuestion(
                    id=q.get("id", f"q-{random.randint(1000, 9999)}"),
                    question=q.get("question", ""),
                    choices=choices,
                    correct=q.get("correct", "A"),
                    clause=q.get("clause", ""),
                    category=q.get("category", "General"),
                    explanation=q.get("explanation"),
                    source=q.get("source", "fallback"),
                )
            )

        return QuizResponse(
            questions=quiz_questions,
            total_available=len(all_questions),
            source_status="fallback",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate quiz: {str(e)}"
        )


@router.get("/v1/quiz/categories")
async def get_quiz_categories():
    """
    Get available question categories
    """
    try:
        all_questions = get_fallback_quiz_data()
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
