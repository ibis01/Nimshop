import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Seller, Product

# Connect to database
engine = create_engine("sqlite:///./nimshop.db")

# FORCE drop and recreate all tables to match your Python models exactly
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✅ Database schema created successfully (including expires_at).")

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Seed Seller
seller = Seller(
    id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
    name="Nimiq Gear Store",
    nimiq_address="NQ07 0000 0000 0000 0000 0000 0000 0000 0000",
    is_active=True
)
db.add(seller)
db.commit()

# Seed Real Products
products_data = [
    {"name": "Sony WH-1000XM5", "price_luna": 34000000, "category": "headphones"},
    {"name": "Apple AirPods Pro", "price_luna": 24000000, "category": "headphones"},
    {"name": "Keychron K2 V2", "price_luna": 8900000, "category": "keyboards"},
    {"name": "Logitech MX Master 3S", "price_luna": 9900000, "category": "mice"},
]

for p in products_data:
    prod = Product(
        id=uuid.uuid4(), seller_id=seller.id, name=p["name"],
        description="Premium real-world product", category=p["category"],
        price_luna=p["price_luna"], currency="NIM",
        attributes={}, inventory_quantity=10, is_active=True,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
    )
    db.add(prod)

db.commit()
print("✅ Products seeded successfully.")
db.close()
