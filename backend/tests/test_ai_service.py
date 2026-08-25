import pytest
from services.ai_service import ai_service, AIExtractionError
from schemas import AIIntent


def test_mock_extraction_headphones():
    intent = ai_service._mock_extract("wireless headphones under 50 NIM with noise cancellation")
    assert intent.category == "headphones"
    assert intent.max_price_luna == 5_000_000
    assert intent.attributes.get("wireless") is True
    assert intent.attributes.get("noise_cancelling") is True


def test_mock_extraction_keyboard():
    intent = ai_service._mock_extract("mechanical keyboard")
    assert intent.category == "keyboards"
    assert intent.attributes.get("mechanical") is True


def test_mock_extraction_no_match():
    intent = ai_service._mock_extract("something random")
    assert intent.category is None
    assert intent.max_price_luna is None


def test_ai_intent_validation():
    # Valid
    intent = AIIntent(category="headphones", max_price_luna=5_000_000)
    assert intent.category == "headphones"

    # Invalid negative price
    with pytest.raises(Exception):
        AIIntent(max_price_luna=-100)

    # Invalid attribute type
    with pytest.raises(Exception):
        AIIntent(attributes={"bad": {"nested": "object"}})