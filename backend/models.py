import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Index, JSON, Uuid
)
from sqlalchemy.orm import relationship
from database import Base


class Seller(Base):
    __tablename__ = "sellers"

    # Uuid is cross-dialect compatible (works in both SQLite and PostgreSQL)
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    nimiq_address = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    products = relationship("Product", back_populates="seller")


class Product(Base):
    __tablename__ = "products"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    price_luna = Column(Integer, nullable=False)  # STRICT INTEGER. 1 NIM = 100,000 Luna.
    currency = Column(String(10), nullable=False, default="NIM")
    seller_id = Column(Uuid(as_uuid=True), ForeignKey("sellers.id"), nullable=False)
    inventory_quantity = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    image_url = Column(String(500), nullable=True)
    attributes = Column(JSON, nullable=False, default=dict)  # JSON works in both SQLite and Postgres
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    # CRITICAL 2: Unique constraint prevents the same tx_hash from paying multiple orders
    tx_hash = Column(String(200), nullable=True, unique=True) 
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    product = relationship("Product")