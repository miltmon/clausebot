"""
Test imports to catch path issues before deployment
"""


def test_package_imports():
    """Test that all package imports work correctly"""
    import clausebot_api

    assert clausebot_api.__version__ == "0.1.0"


def test_main_imports():
    """Test main application imports"""
    from clausebot_api import main

    assert hasattr(main, "app")


def test_airtable_imports():
    """Test Airtable data source imports"""
    from clausebot_api.airtable_data_source import (
        test_airtable_connection,
        get_quiz_source,
        get_airtable_health,
    )

    # Test functions exist
    assert callable(test_airtable_connection)
    assert callable(get_quiz_source)
    assert callable(get_airtable_health)


def test_quiz_core_imports():
    """Test quiz core functionality imports"""
    from clausebot_api.core.quiz import (
        FALLBACK_QUESTIONS,
        get_fallback_questions,
        format_quiz_response,
    )

    # Test fallback questions exist
    assert len(FALLBACK_QUESTIONS) > 0
    assert callable(get_fallback_questions)
    assert callable(format_quiz_response)


def test_fallback_questions_structure():
    """Test that fallback questions have correct structure"""
    from clausebot_api.core.quiz import FALLBACK_QUESTIONS

    for question in FALLBACK_QUESTIONS:
        required_fields = [
            "id",
            "question",
            "choices",
            "correct",
            "clause",
            "category",
            "source",
        ]
        for field in required_fields:
            assert field in question, f"Missing field: {field}"

        assert len(question["choices"]) == 4, "Each question should have 4 choices"
        assert question["correct"] in ["A", "B", "C", "D"], (
            "Correct answer should be A, B, C, or D"
        )
        assert question["source"] == "fallback", "Source should be 'fallback'"


def test_airtable_health_function():
    """Test Airtable health check function"""
    from clausebot_api.airtable_data_source import get_airtable_health

    health = get_airtable_health()

    required_fields = ["service", "status", "configured"]
    for field in required_fields:
        assert field in health, f"Missing health field: {field}"

    assert health["service"] == "airtable"
    assert health["status"] in ["connected", "disconnected"]
