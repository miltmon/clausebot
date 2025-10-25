from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
from pathlib import Path

router = APIRouter()


def load_synonyms() -> Dict[str, List[str]]:
    """Load synonyms for query expansion"""
    try:
        config_dir = Path(__file__).resolve().parents[2] / "config"
        synonyms_file = config_dir / "synonyms.json"

        if synonyms_file.exists():
            with open(synonyms_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("synonyms", {})
    except Exception as e:
        print(f"Error loading synonyms: {e}")

    return {}


def expand_query_with_synonyms(query: str) -> str:
    """Expand query with synonyms for better matching"""
    synonyms = load_synonyms()
    expanded_terms = [query]  # Start with original query

    query_lower = query.lower()
    for key, values in synonyms.items():
        if key in query_lower:
            expanded_terms.extend(values)
        for value in values:
            if value in query_lower:
                expanded_terms.append(key)
                expanded_terms.extend([v for v in values if v != value])
                break

    # Remove duplicates and join
    unique_terms = list(set(expanded_terms))
    return " ".join(unique_terms)


class ChatRequest(BaseModel):
    query: str
    source: Optional[str] = "supabase"
    limit: int = 5


class QAItem(BaseModel):
    id: str
    question: str
    answer: str
    clause_reference: str
    explanation: Optional[str] = None
    image_url: Optional[str] = None
    metadata: Dict = {}


class ChatResponse(BaseModel):
    query: str
    results: List[QAItem]


def search_local_questions(query: str, limit: int = 5) -> List[Dict]:
    """Search questions in local JSON files until Supabase is connected"""
    results = []

    # Expand query with synonyms for better matching
    expanded_query = expand_query_with_synonyms(query)

    # Look for our sample questions file
    workspace_root = (
        Path(__file__).resolve().parents[3]
    )  # Go up to MiltmonNDT_Workspace
    sample_file = workspace_root / "aws_d11_2025_sample_questions.json"

    if sample_file.exists():
        try:
            with open(sample_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                base_data = data.get("aws_d1_1_2025_sample_questions", {})
                questions = base_data.get("questions", [])

                # Add Clause 2 definitions
                clause_2_defs = base_data.get("clause_2_definitions", [])
                questions.extend(clause_2_defs)

                # Add NBIC preview items (marked as preview)
                nbic_previews = base_data.get("nbic_preview_items", [])
                questions.extend(nbic_previews)

                # Enhanced keyword search with synonyms
                query_lower = query.lower()
                expanded_lower = expanded_query.lower()
                for q in questions:
                    question_text = q.get("question", "").lower()
                    clause_ref = q.get("clause_reference", "").lower()
                    keywords = " ".join(q.get("secondary_keywords", [])).lower()

                    if (
                        query_lower in question_text
                        or query_lower in clause_ref
                        or query_lower in keywords
                        or any(word in question_text for word in query_lower.split())
                        or any(word in question_text for word in expanded_lower.split())
                        or any(word in keywords for word in expanded_lower.split())
                    ):
                        results.append(
                            {
                                "id": q.get("question_id", ""),
                                "question": q.get("question", ""),
                                "answer": q.get(
                                    f"choice_{q.get('correct_answer', 'a').lower()}", ""
                                ),
                                "clause_reference": q.get("clause_reference", ""),
                                "explanation": q.get("answer_rationale", ""),
                                "image_url": q.get("image_url"),
                                "metadata": {
                                    "difficulty": q.get("difficulty"),
                                    "primary_keyword": q.get("primary_keyword"),
                                    "secondary_keywords": q.get(
                                        "secondary_keywords", []
                                    ),
                                    "preview": q.get("preview", False),
                                    "standard": "NBIC"
                                    if q.get("preview")
                                    else "AWS D1.1:2025",
                                },
                            }
                        )

                        if len(results) >= limit:
                            break

        except Exception as e:
            print(f"Error reading sample questions: {e}")

    # If no results from sample file, return a helpful default
    if not results:
        results = [
            {
                "id": "default-001",
                "question": f"Query about: {query}",
                "answer": "This is a placeholder response while the database is being set up.",
                "clause_reference": "AWS D1.1:2025",
                "explanation": f"I understand you're asking about \"{query}\". The ClauseBot system is currently using sample data. Once connected to the full database, I'll be able to provide detailed clause interpretations and references.",
                "image_url": None,
                "metadata": {"source": "local_fallback"},
            }
        ]

    return results


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Chat endpoint that searches for relevant Q&A content
    Currently uses local sample data, will integrate with Supabase later
    """
    try:
        # For now, use local search function
        # TODO: Replace with actual Supabase query when connected
        hits = search_local_questions(req.query or "", req.limit)

        # Convert to QAItem format
        results = []
        for hit in hits:
            results.append(
                QAItem(
                    id=hit["id"],
                    question=hit["question"],
                    answer=hit["answer"],
                    clause_reference=hit["clause_reference"],
                    explanation=hit["explanation"],
                    image_url=hit["image_url"],
                    metadata=hit["metadata"],
                )
            )

        return ChatResponse(query=req.query or "", results=results or [])

    except Exception:
        # Return empty results instead of 500 error for better UX
        return ChatResponse(query=req.query or "", results=[])


@router.get("/chat/health")
async def chat_health():
    """Health check for chat system"""
    try:
        workspace_root = Path(__file__).resolve().parents[3]
        sample_file = workspace_root / "aws_d11_2025_sample_questions.json"

        return {
            "status": "operational",
            "sample_data_available": sample_file.exists(),
            "sample_file_path": str(sample_file),
            "supabase_connected": False,  # TODO: Check actual Supabase connection
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "sample_data_available": False,
            "supabase_connected": False,
        }
