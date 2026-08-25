"""
Deterministic seed data for development.
All sellers and products are clearly marked as DEMO.
"""
import uuid
from database import SessionLocal, init_db
from models import Seller, Product


def seed():
    init_db()
    db = SessionLocal()

    # Clear existing data
    db.query(Product).delete()
    db.query(Seller).delete()
    db.commit()

    # Demo Sellers
    seller1 = Seller(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        name="Nimiq Gear Demo",
        nimiq_address="NQ07 0000 0000 0000 0000",
        is_active=True,
    )
    seller2 = Seller(
        id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        name="Tech Haven Demo",
        nimiq_address="NQ08 0000 0000 0000 0000",
        is_active=True,
    )
    db.add_all([seller1, seller2])
    db.commit()

    # Demo Products
    products = [
        Product(
            name="SoundCore X1 Wireless",
            description="Premium wireless headphones with active noise cancellation.",
            category="headphones",
            price_luna=4_200_000,  # 42 NIM
            seller_id=seller1.id,
            inventory_quantity=15,
            is_active=True,
            attributes={"wireless": True, "noise_cancelling": True, "battery_hours": 30},
        ),
        Product(
            name="AudioPro Basic",
            description="Wired headphones with clear sound.",
            category="headphones",
            price_luna=1_500_000,  # 15 NIM
            seller_id=seller1.id,
            inventory_quantity=25,
            is_active=True,
            attributes={"wireless": False, "noise_cancelling": False},
        ),
        Product(
            name="TypeMaster Mechanical",
            description="Full-size mechanical keyboard with blue switches.",
            category="keyboards",
            price_luna=6_800_000,  # 68 NIM
            seller_id=seller2.id,
            inventory_quantity=10,
            is_active=True,
            attributes={"mechanical": True, "wireless": False, "rgb": True},
        ),
        Product(
            name="SlimType Wireless",
            description="Low-profile wireless keyboard for productivity.",
            category="keyboards",
            price_luna=4_500_000,  # 45 NIM
            seller_id=seller2.id,
            inventory_quantity=20,
            is_active=True,
            attributes={"mechanical": False, "wireless": True, "rgb": False},
        ),
        Product(
            name="GlidePro Mouse",
            description="Ergonomic wireless mouse with high DPI.",
            category="mice",
            price_luna=3_200_000,  # 32 NIM
            seller_id=seller1.id,
            inventory_quantity=30,
            is_active=True,
            attributes={"wireless": True, "ergonomic": True},
        ),
        Product(
            name="ClearView 27 Monitor",
            description="27-inch 4K IPS monitor.",
            category="monitors",
            price_luna=15_000_000,  # 150 NIM
            seller_id=seller2.id,
            inventory_quantity=5,
            is_active=True,
            attributes={"size_inches": 27, "resolution": "4K", "ips": True},
        ),
        Product(
            name="BudgetView 24 Monitor",
            description="24-inch 1080p monitor for everyday use.",
            category="monitors",
            price_luna=8_500_000,  # 85 NIM
            seller_id=seller2.id,
            inventory_quantity=12,
            is_active=True,
            attributes={"size_inches": 24, "resolution": "1080p", "ips": False},
        ),
        Product(
            name="SoundCore X1 (Out of Stock)",
            description="Demo out-of-stock product.",
            category="headphones",
            price_luna=4_200_000,
            seller_id=seller1.id,
            inventory_quantity=0,  # Should be filtered out
            is_active=True,
            attributes={"wireless": True, "noise_cancelling": True},
        ),
    ]

    db.add_all(products)
    db.commit()
    db.close()
    print(f"✅ Seeded 2 sellers and {len(products)} products")


if __name__ == "__main__":
    seed()