from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import json
from pathlib import Path

router = APIRouter()


def search_clauses_by_reference(ref: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for clauses by reference in local data until Supabase is connected"""
    results = []

    # Look for our sample questions file
    workspace_root = Path(__file__).resolve().parents[3]
    sample_file = workspace_root / "aws_d11_2025_sample_questions.json"

    if sample_file.exists():
        try:
            with open(sample_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                questions = data.get("aws_d1_1_2025_sample_questions", {}).get(
                    "questions", []
                )

                # Search by clause reference
                ref_lower = ref.lower()
                for q in questions:
                    clause_ref = q.get("clause_reference", "").lower()

                    if (
                        ref_lower in clause_ref
                        or any(
                            part.strip() in clause_ref for part in ref_lower.split(",")
                        )
                        or any(
                            part.strip() in clause_ref for part in ref_lower.split(".")
                        )
                    ):
                        results.append(
                            {
                                "question_id": q.get("question_id", ""),
                                "clause_reference": q.get("clause_reference", ""),
                                "question": q.get("question", ""),
                                "explanation": q.get("answer_rationale", ""),
                                "difficulty": q.get("difficulty"),
                                "primary_keyword": q.get("primary_keyword"),
                                "secondary_keywords": q.get("secondary_keywords", []),
                            }
                        )

                        if len(results) >= limit:
                            break

        except Exception as e:
            print(f"Error reading clause data: {e}")

    return results


@router.get("/clauses/{ref}")
async def get_clause(ref: str):
    """
    Get clause information by reference
    Examples: /v1/clauses/6.12, /v1/clauses/Table%206.1, /v1/clauses/4.2.3
    """
    try:
        # Clean up the reference for better matching
        clean_ref = ref.replace("%20", " ").strip()

        hits = search_clauses_by_reference(clean_ref, 10)

        if not hits:
            raise HTTPException(
                status_code=404,
                detail=f"No clauses found matching reference: {clean_ref}",
            )

        return {"ref": clean_ref, "total_hits": len(hits), "hits": hits}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving clause: {str(e)}"
        )


@router.get("/clauses")
async def list_clauses():
    """List all available clause references"""
    try:
        workspace_root = Path(__file__).resolve().parents[3]
        sample_file = workspace_root / "aws_d11_2025_sample_questions.json"

        clause_refs = set()

        if sample_file.exists():
            with open(sample_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                questions = data.get("aws_d1_1_2025_sample_questions", {}).get(
                    "questions", []
                )

                for q in questions:
                    ref = q.get("clause_reference", "")
                    if ref:
                        clause_refs.add(ref)

        return {
            "total_clauses": len(clause_refs),
            "clause_references": sorted(list(clause_refs)),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing clauses: {str(e)}")


@router.get("/clauses/search/{term}")
async def search_clauses(term: str, limit: int = 5):
    """
    Search clauses by term or keyword
    Examples: /v1/clauses/search/preheat, /v1/clauses/search/visual
    """
    try:
        workspace_root = Path(__file__).resolve().parents[3]
        sample_file = workspace_root / "aws_d11_2025_sample_questions.json"

        results = []

        if sample_file.exists():
            with open(sample_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                questions = data.get("aws_d1_1_2025_sample_questions", {}).get(
                    "questions", []
                )

                term_lower = term.lower()
                for q in questions:
                    question_text = q.get("question", "").lower()
                    explanation = q.get("answer_rationale", "").lower()
                    keywords = " ".join(q.get("secondary_keywords", [])).lower()
                    primary_keyword = q.get("primary_keyword", "").lower()

                    if (
                        term_lower in question_text
                        or term_lower in explanation
                        or term_lower in keywords
                        or term_lower in primary_keyword
                    ):
                        results.append(
                            {
                                "question_id": q.get("question_id", ""),
                                "clause_reference": q.get("clause_reference", ""),
                                "question": q.get("question", ""),
                                "explanation": q.get("answer_rationale", ""),
                                "primary_keyword": q.get("primary_keyword"),
                                "match_score": 1.0,  # Simple scoring for now
                            }
                        )

                        if len(results) >= limit:
                            break

        return {"search_term": term, "total_hits": len(results), "hits": results}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching clauses: {str(e)}"
        )
