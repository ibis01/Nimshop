import uuid
from datetime import datetime, timezone

from database import engine, Base, SessionLocal
from models import Seller, Product

def seed():
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
            {"name": "Sony WH-1000XM5", "price_luna": 34000000, "category": "headphones", "description": "Industry-leading noise canceling.", "attributes": {"wireless": True}},
            {"name": "Apple AirPods Pro", "price_luna": 24000000, "category": "headphones", "description": "Active Noise Cancellation.", "attributes": {"wireless": True}},
            {"name": "Bose QuietComfort 45", "price_luna": 32000000, "category": "headphones", "description": "Wireless noise cancelling.", "attributes": {"wireless": True}},
            {"name": "Sennheiser HD 660S", "price_luna": 49000000, "category": "headphones", "description": "Open-back audiophile headphones.", "attributes": {"wireless": False}},
            {"name": "Keychron K2 V2", "price_luna": 8900000, "category": "keyboards", "description": "Wireless mechanical keyboard.", "attributes": {"wireless": True}},
            {"name": "Logitech MX Keys", "price_luna": 10000000, "category": "keyboards", "description": "Wireless illuminated keyboard.", "attributes": {"wireless": True}},
            {"name": "Corsair K95 RGB", "price_luna": 19900000, "category": "keyboards", "description": "Premium mechanical gaming keyboard.", "attributes": {"wireless": False}},
            {"name": "Logitech MX Master 3S", "price_luna": 9900000, "category": "mice", "description": "Wireless performance mouse.", "attributes": {"wireless": True}},
            {"name": "Razer DeathAdder V3", "price_luna": 14900000, "category": "mice", "description": "Wireless esports gaming mouse.", "attributes": {"wireless": True}},
            {"name": "Logitech G502", "price_luna": 12900000, "category": "mice", "description": "Wireless gaming mouse.", "attributes": {"wireless": True}},
            {"name": "LG 27GP950-B", "price_luna": 79900000, "category": "monitors", "description": "27-inch 4K UHD gaming monitor.", "attributes": {"resolution": "4K"}},
            {"name": "Dell UltraSharp U2720Q", "price_luna": 64900000, "category": "monitors", "description": "27-inch 4K USB-C monitor.", "attributes": {"resolution": "4K"}},
            {"name": "Samsung Odyssey G7", "price_luna": 69900000, "category": "monitors", "description": "32-inch curved QHD monitor.", "attributes": {"resolution": "1440p"}},
            {"name": "Anker 737 Power Bank", "price_luna": 14900000, "category": "accessories", "description": "24,000mAh 140W portable charger.", "attributes": {}},
            {"name": "Elgato Stream Deck", "price_luna": 15900000, "category": "accessories", "description": "15 customizable LCD keys.", "attributes": {}}
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
