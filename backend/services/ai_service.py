import json
import logging
from typing import Optional
from config import settings
from schemas import AIIntent

logger = logging.getLogger(__name__)


class AIExtractionError(Exception):
    pass


class AIService:
    """
    AI abstraction for intent extraction.
    Treated as UNTRUSTED INPUT — output is always validated via Pydantic.
    """

    def __init__(self):
        self.provider = settings.ai_provider

    async def extract_intent(self, query: str) -> AIIntent:
        if self.provider == "mock":
            return self._mock_extract(query)
        elif self.provider == "openai":
            return await self._openai_extract(query)
        else:
            raise AIExtractionError(f"Unknown AI provider: {self.provider}")

    def _mock_extract(self, query: str) -> AIIntent:
        """Deterministic mock for testing and development."""
        q = query.lower()

        # Category detection
        category = None
        category_map = {
            "headphone": "headphones",
            "keyboard": "keyboards",
            "mouse": "mice",
            "monitor": "monitors",
        }
        for keyword, cat in category_map.items():
            if keyword in q:
                category = cat
                break

        # Price detection (assumes "NIM" in query)
        max_price_luna = None
        import re
        price_match = re.search(r"(\d+)\s*nim", q)
        if price_match:
            max_price_luna = int(price_match.group(1)) * 100_000

        # Attribute detection
        attributes = {}
        if "wireless" in q:
            attributes["wireless"] = True
        if "noise" in q and "cancel" in q:
            attributes["noise_cancelling"] = True
        if "mechanical" in q:
            attributes["mechanical"] = True

        return AIIntent(
            category=category,
            max_price_luna=max_price_luna,
            attributes=attributes,
        )
    async def _openai_extract(self, query: str) -> AIIntent:
        """Real OpenAI integration. Output is strictly validated."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)

            system_prompt = (
                "You are an intent extractor for a product catalog. "
                "Extract structured intent as JSON only. "
                "Fields: category (string|null), max_price_luna (integer|null, 1 NIM = 100000 Luna), "
                "min_price_luna (integer|null), attributes (object with boolean/string values), "
                "sort_preference (one of: best_value, lowest_price, highest_price, or null). "
                "Return ONLY valid JSON. No explanation."
            )

            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
                timeout=10,
            )

            raw = response.choices[0].message.content
            if raw is None:
                raise AIExtractionError("Empty response from AI")
            
            parsed = json.loads(raw)
            return AIIntent(**parsed)

        except Exception as e:
            logger.warning(f"OpenAI extraction failed: {e}")
            raise AIExtractionError(str(e))


ai_service = AIService()