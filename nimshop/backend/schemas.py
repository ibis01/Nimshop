import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator


# ---------- AI Intent Schema (strict, untrusted input) ----------

class AIIntent(BaseModel):
    category: Optional[str] = None
    max_price_luna: Optional[int] = Field(default=None, ge=0)
    min_price_luna: Optional[int] = Field(default=None, ge=0)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    sort_preference: Optional[str] = Field(default=None, pattern="^(best_value|lowest_price|highest_price)$")

    @field_validator("attributes")
    @classmethod
    def validate_attributes(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        # Only allow primitive types to prevent injection
        allowed = (str, int, float, bool, type(None))
        for key, value in v.items():
            if not isinstance(key, str) or len(key) > 100:
                raise ValueError("Invalid attribute key")
            if not isinstance(value, allowed):
                raise ValueError(f"Invalid attribute value type for {key}")
        return v


# ---------- API Request/Response ----------

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty")
        return v


class SellerSummary(BaseModel):
    id: uuid.UUID
    name: str


class ProductResult(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    price_luna: int
    category: str
    attributes: Dict[str, Any]
    seller: SellerSummary
    availability: bool
    match_score: float = Field(ge=0.0, le=1.0)


class SearchResponse(BaseModel):
    query: str
    results: List[ProductResult]
    intent: Optional[AIIntent] = None
    used_fallback: bool = False


class HealthResponse(BaseModel):
    status: str
    service: str

# ... (keep existing schemas) ...

class OrderRequest(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(ge=1, le=10)

class OrderIntentResponse(BaseModel):
    order_id: uuid.UUID
    recipient: str
    amount_luna: int
    memo: str

class OrderVerifyRequest(BaseModel):
    order_id: uuid.UUID
    tx_hash: str

class OrderStatusResponse(BaseModel):
    order_id: uuid.UUID
    status: str
    tx_hash: Optional[str] = None