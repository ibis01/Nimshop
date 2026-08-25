from typing import List, Dict, Any, cast
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from models import Product, Seller
from schemas import AIIntent, ProductResult, SellerSummary

WEIGHT_CATEGORY = 0.30
WEIGHT_ATTRIBUTES = 0.30
WEIGHT_BUDGET = 0.25
WEIGHT_AVAILABILITY = 0.10
WEIGHT_VALUE = 0.05

def search_catalog(db: Session, intent: AIIntent, limit: int = 20) -> List[ProductResult]:
    filters = [Product.is_active == True, Product.inventory_quantity > 0]
    if intent.category:
        filters.append(Product.category.ilike(f"%{intent.category}%"))
    if intent.max_price_luna is not None:
        filters.append(Product.price_luna <= intent.max_price_luna)
    if intent.min_price_luna is not None:
        filters.append(Product.price_luna >= intent.min_price_luna)

    stmt = (
        select(Product, Seller)
        .join(Seller, Product.seller_id == Seller.id)
        .where(and_(*filters))
        .where(Seller.is_active == True)
        .limit(limit * 3)
    )
    rows = db.execute(stmt).all()

    scored = [(_compute_score(product, intent), product, seller) for product, seller in rows]
    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        ProductResult(
            id=product.id, name=product.name, description=product.description,
            price_luna=product.price_luna, category=product.category,
            attributes=product.attributes or {},
            seller=SellerSummary(id=seller.id, name=seller.name),
            availability=product.inventory_quantity > 0,
            match_score=round(score, 3),
        )
        for score, product, seller in scored[:limit]
    ]

def _compute_score(product: Product, intent: AIIntent) -> float:
    category_str = str(product.category) if product.category else ""
    attributes_dict: Dict[str, Any] = cast(Dict[str, Any], product.attributes) or {}
    price_luna_float = float(product.price_luna)
    inventory_qty_int = int(product.inventory_quantity)

    scores: Dict[str, float] = {}
    scores["category"] = 1.0 if intent.category and intent.category.lower() in category_str.lower() else 0.5
    
    if intent.attributes:
        matches = sum(1 for k, v in intent.attributes.items() if attributes_dict.get(k) == v)
        total = len(intent.attributes)
        scores["attributes"] = float(matches) / float(total) if total > 0 else 0.5
    else:
        scores["attributes"] = 0.5

    if intent.max_price_luna and intent.max_price_luna > 0:
        max_price = float(intent.max_price_luna)
        ratio = price_luna_float / max_price
        scores["budget"] = max(0.0, 1.0 - abs(1.0 - ratio))
        scores["value"] = 1.0 - (price_luna_float / max_price)
    else:
        scores["budget"] = 0.5
        scores["value"] = 0.5

    scores["availability"] = 1.0 if inventory_qty_int > 0 else 0.0

    return float(
        scores["category"] * WEIGHT_CATEGORY +
        scores["attributes"] * WEIGHT_ATTRIBUTES +
        scores["budget"] * WEIGHT_BUDGET +
        scores["availability"] * WEIGHT_AVAILABILITY +
        scores["value"] * WEIGHT_VALUE
    )