import json
import uuid
import requests
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Seller, Product

# --- STEP A: Fix Database Schema ---
print("🔧 Fixing database schema...")
engine = create_engine("sqlite:///./nimshop.db")
Base.metadata.create_all(bind=engine) # Creates tables with 'expires_at'

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# --- STEP B: Seed Real Products ---
print("🌱 Seeding real products...")
seller = db.query(Seller).first()
if not seller:
    seller = Seller(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        name="Nimiq Gear Store",
        nimiq_address="NQ07 0000 0000 0000 0000 0000 0000 0000 0000",
        is_active=True
    )
    db.add(seller)
    db.commit()

products_data = [
    {"name": "Sony WH-1000XM5", "price_luna": 34000000, "category": "headphones"},
    {"name": "Apple AirPods Pro", "price_luna": 24000000, "category": "headphones"},
    {"name": "Keychron K2 V2", "price_luna": 8900000, "category": "keyboards"},
    {"name": "Logitech MX Master 3S", "price_luna": 9900000, "category": "mice"},
]

valid_product_id = None
for p in products_data:
    prod = Product(
        id=uuid.uuid4(), seller_id=seller.id, name=p["name"],
        description="Real product", category=p["category"],
        price_luna=p["price_luna"], currency="NIM",
        attributes={}, inventory_quantity=10, is_active=True,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    db.add(prod)
    if valid_product_id is None:
        valid_product_id = str(prod.id) # Save the first ID

db.commit()
print(f"✅ Seeded products. Valid ID: {valid_product_id}")
db.close()

# --- STEP C: Create Order via API ---
print("🛒 Creating order via API...")
response = requests.post(
    "http://localhost:8000/api/orders",
    json={"product_id": valid_product_id, "quantity": 1}
)
if response.status_code == 200:
    print(" SUCCESS! Order created:")
    print(response.json())
else:
    print(f"❌ Failed: {response.text}")
