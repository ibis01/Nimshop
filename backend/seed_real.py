import json
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Seller, Product

# Force creation of ALL tables with the latest schema (including expires_at)
engine = create_engine("sqlite:///./nimshop.db")
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Create seller
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

# Load and seed products
with open('products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

count = 0
for p in products:
    product = Product(
        id=uuid.uuid4(),
        seller_id=seller.id,
        name=p.get("name"),
        description=p.get("description", ""),
        category=p.get("category", "general").lower(),
        price_luna=int(p.get("price_luna", 0)),
        currency="NIM",
        attributes=p.get("attributes", {}),
        inventory_quantity=int(p.get("inventory", 10)),
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(product)
    count += 1

db.commit()
print(f"✅ Successfully seeded {count} real products with correct schema!")
db.close()
