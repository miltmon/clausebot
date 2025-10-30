"""
Quiz core functionality and fallback data
"""

from typing import List, Dict, Any

# Fallback quiz questions for when Airtable is unavailable
FALLBACK_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": "fallback-undercut-1",
        "question": "According to AWS D1.1, what is the maximum allowable undercut depth for statically loaded members?",
        "choices": [
            "1/32 inch (0.8 mm)",
            "1/16 inch (1.6 mm)",
            "3/32 inch (2.4 mm)",
            "1/8 inch (3.2 mm)",
        ],
        "correct": "A",
        "clause": "AWS D1.1 Clause 6.9.1",
        "category": "Visual Inspection",
        "explanation": "For statically loaded members, undercut shall not exceed 1/32 inch (0.8 mm) in depth according to AWS D1.1 Clause 6.9.1.",
        "source": "fallback",
    },
    {
        "id": "fallback-joint-prep-1",
        "question": "What is the primary purpose of joint preparation in welding according to AWS D1.1?",
        "choices": [
            "To improve appearance",
            "To ensure proper penetration and fusion",
            "To reduce welding time",
            "To minimize material usage",
        ],
        "correct": "B",
        "clause": "AWS D1.1 Clause 2.3",
        "category": "Joint Preparation",
        "explanation": "Joint preparation ensures proper penetration and fusion, which is critical for weld quality and structural integrity.",
        "source": "fallback",
    },
    {
        "id": "fallback-preheat-1",
        "question": "What is the minimum preheat temperature for welding ASTM A514 steel with thickness greater than 2.5 inches?",
        "choices": ["200°F (93°C)", "300°F (149°C)", "400°F (204°C)", "500°F (260°C)"],
        "correct": "C",
        "clause": "AWS D1.1 Clause 3.3.2",
        "category": "Preheat",
        "explanation": "AWS D1.1 requires 400°F minimum preheat for A514 steel over 2.5 inches thick to prevent cracking.",
        "source": "fallback",
    },
    {
        "id": "fallback-process-1",
        "question": "Which welding process requires the most restrictive joint preparation according to AWS D1.1?",
        "choices": ["SMAW", "GMAW", "FCAW", "SAW"],
        "correct": "D",
        "clause": "AWS D1.1 Clause 2.3",
        "category": "Joint Preparation",
        "explanation": "Submerged Arc Welding (SAW) requires the most precise joint preparation due to its high deposition rates and penetration characteristics.",
        "source": "fallback",
    },
    {
        "id": "fallback-inspection-1",
        "question": "What is the minimum size of discontinuity that must be reported during visual inspection?",
        "choices": [
            "1/16 inch (1.6 mm)",
            "1/8 inch (3.2 mm)",
            "3/16 inch (4.8 mm)",
            "Any visible discontinuity",
        ],
        "correct": "D",
        "clause": "AWS D1.1 Clause 6.9",
        "category": "Visual Inspection",
        "explanation": "All visible discontinuities must be evaluated against the acceptance criteria, regardless of size.",
        "source": "fallback",
    },
]


def get_fallback_questions(count: int = 5) -> List[Dict[str, Any]]:
    """Get fallback quiz questions"""
    return FALLBACK_QUESTIONS[:count]


def format_quiz_response(
    questions: List[Dict[str, Any]], source: str = "unknown"
) -> Dict[str, Any]:
    """Format questions into standard quiz response"""
    return {
        "source": source,
        "count": len(questions),
        "total_available": len(questions),
        "questions": questions,
    }
