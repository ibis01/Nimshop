import logging
from sqlalchemy.orm import Session
from models import Product

logger = logging.getLogger(__name__)

def auto_seed_products(db: Session):
    """
    Automatically seed products if database is empty.
    Safe to call on every startup - checks if products already exist.
    """
    try:
        # Check if products already exist
        existing_count = db.query(Product).count()
        if existing_count > 0:
            logger.info(f"✅ Database already has {existing_count} products. Skipping seed.")
            return
        
        # Import and run the seed script
        from seed import seed
        logger.info(" No products found. Running seed script...")
        seed()
        logger.info("✅ Auto-seeding complete.")
        
    except Exception as e:
        logger.error(f"❌ Auto-seeding failed: {e}")
        raise
