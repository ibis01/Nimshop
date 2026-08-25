import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Index, JSON, Uuid
from sqlalchemy.orm import relationship
from database import Base

def get_expiry_time():
    # Returns naive UTC to match SQLite behavior and avoid deprecation warnings
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=15)

class Seller(Base):
    __tablename__ = "sellers"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    nimiq_address = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    products = relationship("Product", back_populates="seller")

class Product(Base):
    __tablename__ = "products"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    price_luna = Column(Integer, nullable=False)
    currency = Column(String(10), nullable=False, default="NIM")
    seller_id = Column(Uuid(as_uuid=True), ForeignKey("sellers.id"), nullable=False)
    inventory_quantity = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    image_url = Column(String(500), nullable=True)
    attributes = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    seller = relationship("Seller", back_populates="products")
    __table_args__ = (
        Index("ix_products_active_instock", "is_active", "inventory_quantity"),
        Index("ix_products_category_active", "category", "is_active"),
    )

class Order(Base):
    __tablename__ = "orders"
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(Uuid(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_luna = Column(Integer, nullable=False)
    recipient_address = Column(String(100), nullable=False)
    memo = Column(String(200), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    tx_hash = Column(String(200), nullable=True, unique=True)
    expires_at = Column(DateTime, nullable=False, default=get_expiry_time)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    product = relationship("Product")