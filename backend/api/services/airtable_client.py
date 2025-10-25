"""
Airtable Client for ClauseBot
Handles live fallback queries when Supabase cache misses
"""

import os
import httpx
from typing import List, Dict, Any, Optional

# Airtable Configuration
API_BASE = "https://api.airtable.com/v0"
API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = os.getenv("AIRTABLE_TABLE", "Questions")

# Request headers
HEADERS = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}


async def airtable_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search Airtable directly for questions (fallback when Supabase cache misses)
    """
    if not all([API_KEY, BASE_ID]):
        print("⚠️  Airtable credentials not configured")
        return []

    try:
        # Create search formula for Airtable
        # Searches in question, explanation, and clause_reference fields
        safe_query = query.replace("'", "''")  # Escape single quotes
        formula = (
            f"OR("
            f"FIND(LOWER('{safe_query}'),LOWER({{question}})),"
            f"FIND(LOWER('{safe_query}'),LOWER({{explanation}})),"
            f"FIND(LOWER('{safe_query}'),LOWER({{clause_reference}}))"
            f")"
        )

        params = {
            "maxRecords": limit,
            "filterByFormula": formula,
            "sort[0][field]": "question_id",
            "sort[0][direction]": "asc",
        }

        url = f"{API_BASE}/{BASE_ID}/{TABLE_NAME}"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=HEADERS, params=params)
            response.raise_for_status()

            data = response.json()
            records = data.get("records", [])

            # Transform to consistent format
            results = []
            for record in records:
                fields = record.get("fields", {})
                if not fields:
                    continue

                # Map Airtable fields to ClauseBot format
                result = {
                    "id": fields.get("question_id") or record.get("id", ""),
                    "question": fields.get("question", ""),
                    "answer": fields.get("correct_option_text")
                    or fields.get("correct_answer", ""),
                    "clause_reference": fields.get("clause_reference", ""),
                    "explanation": fields.get("explanation")
                    or fields.get("answer_rationale", ""),
                    "image_url": fields.get("image_url"),
                    "metadata": {
                        "source": "airtable_live",
                        "difficulty": fields.get("difficulty"),
                        "primary_keyword": fields.get("primary_keyword"),
                        "secondary_keywords": fields.get("secondary_keywords", []),
                        "clause_type": fields.get("clause_type"),
                        "preview": fields.get("preview", False),
                        "airtable_record_id": record.get("id"),
                    },
                }
                results.append(result)

            print(f"📥 Airtable live search: {len(results)} results for '{query}'")
            return results

    except Exception as e:
        print(f"❌ Airtable search error: {e}")
        return []


async def get_airtable_record_by_id(record_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific record from Airtable by ID
    """
    if not all([API_KEY, BASE_ID]):
        return None

    try:
        url = f"{API_BASE}/{BASE_ID}/{TABLE_NAME}/{record_id}"

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()

            record = response.json()
            fields = record.get("fields", {})

            return {
                "id": fields.get("question_id") or record.get("id", ""),
                "question": fields.get("question", ""),
                "answer": fields.get("correct_option_text")
                or fields.get("correct_answer", ""),
                "clause_reference": fields.get("clause_reference", ""),
                "explanation": fields.get("explanation")
                or fields.get("answer_rationale", ""),
                "image_url": fields.get("image_url"),
                "metadata": {
                    "source": "airtable_direct",
                    "difficulty": fields.get("difficulty"),
                    "primary_keyword": fields.get("primary_keyword"),
                    "secondary_keywords": fields.get("secondary_keywords", []),
                    "airtable_record_id": record.get("id"),
                },
            }

    except Exception as e:
        print(f"❌ Airtable record fetch error: {e}")
        return None


async def test_airtable_connection() -> Dict[str, Any]:
    """
    Test Airtable connection and return status
    """
    if not all([API_KEY, BASE_ID]):
        return {
            "connected": False,
            "error": "Missing AIRTABLE_API_KEY or AIRTABLE_BASE_ID",
        }

    try:
        url = f"{API_BASE}/{BASE_ID}/{TABLE_NAME}"
        params = {"maxRecords": 1}

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=HEADERS, params=params)
            response.raise_for_status()

            data = response.json()
            record_count = len(data.get("records", []))

            return {
                "connected": True,
                "base_id": BASE_ID,
                "table_name": TABLE_NAME,
                "sample_records": record_count,
                "api_key_valid": True,
            }

    except Exception as e:
        return {"connected": False, "error": str(e)}


# Synchronous wrapper for compatibility
def airtable_search_sync(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Synchronous wrapper for airtable_search"""
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(airtable_search(query, limit))
