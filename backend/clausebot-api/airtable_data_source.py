"""
Airtable Data Source for ClauseBot Quiz Questions
Connects to the real Airtable base with quiz data
"""

from pyairtable import Table
import os
from typing import Iterator, Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class AirtableDataSource:
    def __init__(self):
        self.token = os.getenv("AIRTABLE_TOKEN")
        self.base_id = os.getenv("AIRTABLE_BASE_ID", "appJQ23u70iwOl5Nn")
        self.table_id = os.getenv("AIRTABLE_TABLE_ID", "tblvvclz8NSpiSVR9")
        self.view_id = os.getenv("AIRTABLE_VIEW_ID", "viw5Q9YwrJ9Saz8ca")

        if not self.token or not self.base_id:
            logger.warning(
                "Missing AIRTABLE_TOKEN or AIRTABLE_BASE_ID - using fallback data"
            )
            self.connected = False
        else:
            self.connected = True
            logger.info(
                f"Airtable connection configured: base={self.base_id}, table={self.table_id}"
            )

    def iter_records(self) -> Iterator[Dict]:
        """Iterate through Airtable records and yield normalized quiz data"""
        if not self.connected:
            # Fallback to sample data if Airtable not configured
            yield from self._get_fallback_data()
            return

        try:
            table = Table(self.token, self.base_id, self.table_id)

            for record in table.iterate(view=self.view_id):
                fields = record["fields"]

                # Normalize the Airtable data to our quiz format
                yield {
                    "id": record["id"],
                    "question": fields.get("Question", ""),
                    "choices": [
                        fields.get("Answer Choice A", ""),
                        fields.get("Answer Choice B", ""),
                        fields.get("Answer Choice C", ""),
                        fields.get("Answer Choice D", ""),
                    ],
                    "correct": fields.get("Correct Answer", ""),
                    "clause": fields.get("Primary Code Reference", ""),
                    "category": fields.get("Question Category", ""),
                    "explanation": fields.get("Explanation of Correct Answer", ""),
                    "source": "airtable",
                }

        except Exception as e:
            logger.error(f"Error fetching from Airtable: {e}")
            # Fallback to sample data on error
            yield from self._get_fallback_data()

    def _get_fallback_data(self) -> Iterator[Dict]:
        """Fallback quiz data when Airtable is not available"""
        fallback_questions = [
            {
                "id": "fallback-1",
                "question": "According to AWS D1.1, what is the maximum allowable undercut depth for statically loaded members?",
                "choices": [
                    "1/32 inch (0.8 mm)",
                    "1/16 inch (1.6 mm)",
                    "1/8 inch (3.2 mm)",
                    "3/32 inch (2.4 mm)",
                ],
                "correct": "A",
                "clause": "6.9.1",
                "category": "Visual Inspection",
                "explanation": "AWS D1.1 Table 6.1 specifies maximum undercut depth of 1/32 inch for statically loaded members.",
                "source": "fallback",
            },
            {
                "id": "fallback-2",
                "question": "What is the minimum preheat temperature for welding ASTM A514 steel with thickness greater than 2.5 inches?",
                "choices": [
                    "200°F (93°C)",
                    "300°F (149°C)",
                    "400°F (204°C)",
                    "500°F (260°C)",
                ],
                "correct": "C",
                "clause": "3.3.2",
                "category": "Preheat",
                "explanation": "AWS D1.1 requires 400°F minimum preheat for A514 steel over 2.5 inches thick.",
                "source": "fallback",
            },
            {
                "id": "fallback-3",
                "question": "Which welding process requires the most restrictive joint preparation according to AWS D1.1?",
                "choices": ["SMAW", "GMAW", "FCAW", "SAW"],
                "correct": "D",
                "clause": "2.3",
                "category": "Joint Preparation",
                "explanation": "Submerged Arc Welding (SAW) requires the most precise joint preparation due to its high deposition rates.",
                "source": "fallback",
            },
        ]

        for question in fallback_questions:
            yield question


def get_quiz_source() -> List[Dict]:
    """Get all quiz questions from Airtable or fallback data"""
    try:
        data_source = AirtableDataSource()
        questions = list(data_source.iter_records())
        logger.info(f"Loaded {len(questions)} quiz questions")
        return questions
    except Exception as e:
        logger.error(f"Error loading quiz data: {e}")
        return []


def test_airtable_connection() -> Dict[str, Any]:
    """Test the Airtable connection and return status"""
    try:
        data_source = AirtableDataSource()
        if not data_source.connected:
            return {
                "status": "disconnected",
                "message": "Airtable credentials not configured",
                "fallback": True,
            }

        # Try to fetch one record to test connection
        questions = list(data_source.iter_records())

        return {
            "status": "connected",
            "message": "Successfully connected to Airtable",
            "questions_count": len(questions),
            "base_id": data_source.base_id,
            "table_id": data_source.table_id,
            "fallback": False,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection failed: {str(e)}",
            "fallback": True,
        }
