import os
import logging
import uuid
from typing import Optional
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from config import settings
from database import get_db, init_db
from models import Order, Product
from schemas import (
    SearchRequest, SearchResponse, HealthResponse, AIIntent,
    OrderRequest, OrderIntentResponse, OrderVerifyRequest, OrderStatusResponse
)
from services.ai_service import ai_service, AIExtractionError
from services.search_service import search_catalog
from services.payment_service import verify_nimiq_transaction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized")
    yield

app = FastAPI(title="NimShop Backend", version="0.4.1", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],  # Permissive for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="healthy", service="nimshop-backend")

@app.post("/api/search", response_model=SearchResponse)
async def search_products(request: SearchRequest, db: Session = Depends(get_db)):
    intent: Optional[AIIntent] = None
    used_fallback = False
    try:
        intent = await ai_service.extract_intent(request.query)
    except AIExtractionError as e:
        logger.warning(f"AI extraction failed, using fallback: {e}")
        intent = ai_service._mock_extract(request.query)
        used_fallback = True
    except Exception as e:
        logger.error(f"Unexpected AI error: {e}")
        intent = ai_service._mock_extract(request.query)
        used_fallback = True

    return SearchResponse(query=request.query, results=search_catalog(db, intent), intent=intent, used_fallback=used_fallback)

@app.post("/api/orders", response_model=OrderIntentResponse)
def create_order(req: OrderRequest, db: Session = Depends(get_db)):
    try:
        product = db.query(Product).with_for_update().filter(
            Product.id == req.product_id, Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found or inactive")
        if req.quantity <= 0:
            raise HTTPException(status_code=400, detail="Invalid quantity")
        if int(product.inventory_quantity) < req.quantity: # type: ignore[arg-type]
            raise HTTPException(status_code=400, detail="Insufficient inventory")

        total_luna = int(product.price_luna) * req.quantity # type: ignore[arg-type]
        order_id = uuid.uuid4()
        memo = f"NIMSHOP:{order_id}"
        recipient = str(product.seller.nimiq_address) # type: ignore[arg-type]

        order = Order(
            id=order_id, product_id=product.id, quantity=req.quantity,
            total_luna=total_luna, recipient_address=recipient, memo=memo, status="pending"
        )
        db.add(order)
        
        # Mypy fix: Explicitly ignore assignment to SQLAlchemy Column attribute
        product.inventory_quantity = int(product.inventory_quantity) - req.quantity # type: ignore[assignment, arg-type]
        if int(product.inventory_quantity) < 0: # type: ignore[arg-type]
            db.rollback()
            raise HTTPException(status_code=400, detail="Inventory race condition detected")
            
        db.commit()
        db.refresh(order)
        return OrderIntentResponse(order_id=order_id, recipient=recipient, amount_luna=total_luna, memo=memo)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Order creation conflict")


@app.post("/api/orders/verify", response_model=OrderStatusResponse)
async def verify_order(req: OrderVerifyRequest, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == req.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if str(order.status) == "paid": # type: ignore[arg-type]
        return OrderStatusResponse(
            order_id=req.order_id, 
            status="paid", 
            tx_hash=str(order.tx_hash) if order.tx_hash else None # type: ignore[arg-type]
        )
        
    # Prevent retroactive payment of cancelled/failed orders
    if order.status in ["cancelled", "failed"]: # type: ignore[operator]
        raise HTTPException(status_code=400, detail="Order is no longer pending")
        
    if order.tx_hash:
        raise HTTPException(status_code=409, detail="Order already has a transaction associated")

    existing_tx = db.query(Order).filter(Order.tx_hash == req.tx_hash).first()
    if existing_tx:
        raise HTTPException(status_code=409, detail="Transaction hash already used")

    # Lazy reservation expiry check
    if str(order.status) == "pending" and order.expires_at < datetime.now(timezone.utc).replace(tzinfo=None): # type: ignore[arg-type]
        order.status = "cancelled" # type: ignore[assignment]
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            product.inventory_quantity = int(product.inventory_quantity) + order.quantity # type: ignore[assignment, arg-type]
        db.commit()
        raise HTTPException(status_code=400, detail="Order reservation expired")

    verification = await verify_nimiq_transaction(
        req.tx_hash, 
        str(order.recipient_address), # type: ignore[arg-type]
        int(order.total_luna), # type: ignore[arg-type]
        str(order.memo), # type: ignore[arg-type]
        settings.nimiq_network
    )

    if verification["valid"]:
        order.status = "paid" # type: ignore[assignment]
        order.tx_hash = req.tx_hash # type: ignore[assignment]
        db.commit()
        return OrderStatusResponse(order_id=req.order_id, status="paid", tx_hash=req.tx_hash)
    else:
        order.status = "failed" # type: ignore[assignment]
        db.commit()
        raise HTTPException(status_code=400, detail=f"Verification failed: {verification['reason']}")