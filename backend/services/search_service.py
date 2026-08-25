import uuid
from typing import List, Optional, Dict, Any, cast
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from models import Product, Seller
from schemas import AIIntent, ProductResult, SellerSummary

# Deterministic ranking weights (sum = 1.0)
WEIGHT_CATEGORY = 0.30
WEIGHT_ATTRIBUTES = 0.30
WEIGHT_BUDGET = 0.25
WEIGHT_AVAILABILITY = 0.10
WEIGHT_VALUE = 0.05


def search_catalog(
    db: Session,
    intent: AIIntent,
    limit: int = 20,
) -> List[ProductResult]:
    """
    Deterministic catalog search.
    AI intent is used ONLY for filtering — never for fabricating data.
    """
    # Build strict DB filters
    filters = [
        Product.is_active == True,
        Product.inventory_quantity > 0,
    ]

    if intent.category:
        filters.append(Product.category.ilike(f"%{intent.category}%"))

    if intent.max_price_luna is not None:
        filters.append(Product.price_luna <= intent.max_price_luna)

    if intent.min_price_luna is not None:
        filters.append(Product.price_luna >= intent.min_price_luna)

    # Execute query
    stmt = (
        select(Product, Seller)
        .join(Seller, Product.seller_id == Seller.id)
        .where(and_(*filters))
        .where(Seller.is_active == True)
        .limit(limit * 3)  # Fetch more for ranking
    )
    rows = db.execute(stmt).all()

    # Score and rank
    scored = []
    for product, seller in rows:
        score = _compute_score(product, intent)
        scored.append((product, seller, score))

    # Sort by score descending
    scored.sort(key=lambda x: x[2], reverse=True)

    # Build response
    results = []
    for product, seller, score in scored[:limit]:
        results.append(ProductResult(
            id=product.id,
            name=product.name,
            description=product.description,
            price_luna=product.price_luna,
            category=product.category,
            attributes=product.attributes or {},
            seller=SellerSummary(id=seller.id, name=seller.name),
            availability=product.inventory_quantity > 0,
            match_score=round(score, 3),
        ))

    return results


def _compute_score(product: Product, intent: AIIntent) -> float:
    """Deterministic scoring. No AI involvement."""
    
    # Explicitly cast SQLAlchemy column attributes to native Python types to satisfy mypy
    category_str = str(product.category) if product.category else ""
    attributes_dict: Dict[str, Any] = cast(Dict[str, Any], product.attributes) or {}
    price_luna_float = float(product.price_luna)
    inventory_qty_int = int(product.inventory_quantity)

    scores: Dict[str, float] = {}

    # 1. Category match (30%)
    if intent.category:
        scores["category"] = 1.0 if intent.category.lower() in category_str.lower() else 0.0
    else:
        scores["category"] = 0.5

    # 2. Attribute match (30%)
    if intent.attributes:
        matches = sum(1 for k, v in intent.attributes.items() if attributes_dict.get(k) == v)
        total = len(intent.attributes)
        scores["attributes"] = float(matches) / float(total) if total > 0 else 0.5
    else:
        scores["attributes"] = 0.5

    # 3. Budget match (25%)
    if intent.max_price_luna and intent.max_price_luna > 0:
        max_price = float(intent.max_price_luna)
        ratio = price_luna_float / max_price
        scores["budget"] = max(0.0, 1.0 - abs(1.0 - ratio))
    else:
        scores["budget"] = 0.5

    # 4. Availability (10%)
    scores["availability"] = 1.0 if inventory_qty_int > 0 else 0.0

    # 5. Value (5%)
    if intent.max_price_luna and intent.max_price_luna > 0:
        max_price = float(intent.max_price_luna)
        scores["value"] = 1.0 - (price_luna_float / max_price)
    else:
        scores["value"] = 0.5

    # Weighted sum
    total_score = (
        scores["category"] * WEIGHT_CATEGORY +
        scores["attributes"] * WEIGHT_ATTRIBUTES +
        scores["budget"] * WEIGHT_BUDGET +
        scores["availability"] * WEIGHT_AVAILABILITY +
        scores["value"] * WEIGHT_VALUE
    )

    return float(total_score)