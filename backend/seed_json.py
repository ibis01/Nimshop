import json
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Seller, Product

# Database setup
engine = create_engine("sqlite:///./nimshop.db")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# 1. Ensure Seller exists
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

# 2. Load your fetched JSON data
# Ensure your file is named 'products.json' and is in the backend directory
with open('products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# 3. Seed the database
count = 0
for p in products:
    # Map your JSON fields to the DB model. 
    # Adjust the .get() keys to match your actual JSON structure!
    product = Product(
        id=uuid.uuid4(),
        seller_id=seller.id,
        name=p.get("name") or p.get("title", "Unknown Product"),
        description=p.get("description", "No description available."),
        category=p.get("category", "general").lower(),
        price_luna=int(p.get("price_luna", p.get("price", 0))), # Ensure it's in Luna (1 NIM = 100,000 Luna)
        currency="NIM",
        attributes=p.get("attributes", p.get("features", {})),
        inventory_quantity=int(p.get("inventory", p.get("stock", 10))),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(product)
    count += 1

db.commit()
print(f"✅ Successfully seeded {count} products from JSON!")
db.close()