import logging
import uuid
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

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
    # Startup
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown


app = FastAPI(title="NimShop Backend", version="0.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="healthy", service="nimshop-backend")


@app.post("/api/search", response_model=SearchResponse)
async def search_products(
    request: SearchRequest,
    db: Session = Depends(get_db),
):
    """
    AI-assisted product search.
    AI is used ONLY for intent extraction — catalog is deterministic.
    """
    intent: Optional[AIIntent] = None
    used_fallback = False

    # Step 1: Extract intent via AI
    try:
        intent = await ai_service.extract_intent(request.query)
    except AIExtractionError as e:
        logger.warning(f"AI extraction failed, using fallback: {e}")
        # Fallback to deterministic mock parser
        intent = ai_service._mock_extract(request.query)
        used_fallback = True
    except Exception as e:
        logger.error(f"Unexpected AI error: {e}")
        intent = ai_service._mock_extract(request.query)
        used_fallback = True

    # Step 2: Deterministic catalog search
    results = search_catalog(db, intent)

    return SearchResponse(
        query=request.query,
        results=results,
        intent=intent,
        used_fallback=used_fallback,
    )


@app.post("/api/orders", response_model=OrderIntentResponse)
def create_order(req: OrderRequest, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == req.product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    if int(product.inventory_quantity) < req.quantity: # type: ignore[arg-type]
        raise HTTPException(status_code=400, detail="Insufficient inventory")

    total_luna = int(product.price_luna) * req.quantity # type: ignore[arg-type]
    order_id = uuid.uuid4()
    memo = f"NIMSHOP:{order_id}"
    recipient = str(product.seller.nimiq_address) # type: ignore[arg-type]

    order = Order(
        id=order_id,
        product_id=product.id,
        quantity=req.quantity,
        total_luna=total_luna,
        recipient_address=recipient,
        memo=memo,
        status="pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return OrderIntentResponse(
        order_id=order_id,
        recipient=recipient,
        amount_luna=total_luna,
        memo=memo
    )


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

    is_valid = await verify_nimiq_transaction(
        req.tx_hash, 
        str(order.recipient_address), # type: ignore[arg-type]
        int(order.total_luna), # type: ignore[arg-type]
        str(order.memo) # type: ignore[arg-type]
    )

    if is_valid:
        order.status = "paid" # type: ignore[assignment]
        order.tx_hash = req.tx_hash # type: ignore[assignment]
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            product.inventory_quantity = int(product.inventory_quantity) - order.quantity # type: ignore[assignment, arg-type]
        db.commit()
        return OrderStatusResponse(order_id=req.order_id, status="paid", tx_hash=req.tx_hash)
    else:
        order.status = "failed" # type: ignore[assignment]
        db.commit()
        raise HTTPException(status_code=400, detail="Transaction verification failed")