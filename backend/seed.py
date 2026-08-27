"""
Authoritative database seeding script.
Usage: python seed.py (from backend directory)
"""
import uuid
from datetime import datetime, timezone

# Strict local imports to match the rest of the backend application
# This prevents SQLAlchemy from registering tables twice under different module names
from database import engine, Base, SessionLocal
from models import Seller, Product

def seed():
    # SAFE: create_all only creates missing tables, it NEVER drops existing data
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        if db.query(Seller).first():
            print("✅ Database already seeded. Skipping to prevent data loss.")
            return

        seller = Seller(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            name="Nimiq Gear Store",
            nimiq_address="NQ07 0000 0000 0000 0000 0000 0000 0000 0000",
            is_active=True
        )
        db.add(seller)
        db.commit()

        products_data = [
            {"name": "Sony WH-1000XM5", "price_luna": 34000000, "category": "headphones", "description": "Industry-leading noise canceling wireless headphones.", "attributes": {"wireless": True, "noise_cancelling": True}},
            {"name": "Apple AirPods Pro", "price_luna": 24000000, "category": "headphones", "description": "Active Noise Cancellation, Adaptive Transparency.", "attributes": {"wireless": True, "noise_cancelling": True}},
            {"name": "Keychron K2 V2", "price_luna": 8900000, "category": "keyboards", "description": "Wireless mechanical keyboard with RGB backlight.", "attributes": {"wireless": True, "mechanical": True}},
            {"name": "Logitech MX Master 3S", "price_luna": 9900000, "category": "mice", "description": "Wireless performance mouse with 8K DPI sensor.", "attributes": {"wireless": True, "ergonomic": True}},
        ]

        for p in products_data:
            prod = Product(
                id=uuid.uuid4(), seller_id=seller.id, name=p["name"],
                description=p["description"], category=p["category"],
                price_luna=p["price_luna"], currency="NIM",
                attributes=p["attributes"], inventory_quantity=10,
                is_active=True, created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(prod)
        
        db.commit()
        print(f"✅ Successfully seeded {len(products_data)} products.")
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
