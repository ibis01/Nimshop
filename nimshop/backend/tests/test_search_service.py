import pytest
from services.search_service import search_catalog
from schemas import AIIntent
from seed import seed


@pytest.fixture(autouse=True)
def seed_db(db_session):
    """Seed test DB before each test."""
    # Use in-memory seed for tests
    from models import Seller, Product
    import uuid

    seller = Seller(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        name="Demo Seller",
        nimiq_address="NQ00 DEMO",
        is_active=True,
    )
    db_session.add(seller)

    products = [
        Product(
            name="Wireless Headphones",
            description="Wireless with noise cancellation",
            category="headphones",
            price_luna=4_200_000,
            seller_id=seller.id,
            inventory_quantity=10,
            attributes={"wireless": True, "noise_cancelling": True},
        ),
        Product(
            name="Wired Headphones",
            description="Basic wired",
            category="headphones",
            price_luna=1_500_000,
            seller_id=seller.id,
            inventory_quantity=5,
            attributes={"wireless": False},
        ),
        Product(
            name="Out of Stock Headphones",
            description="Should be filtered",
            category="headphones",
            price_luna=4_200_000,
            seller_id=seller.id,
            inventory_quantity=0,
            attributes={"wireless": True},
        ),
    ]
    db_session.add_all(products)
    db_session.commit()


def test_category_filter(db_session):
    intent = AIIntent(category="headphones")
    results = search_catalog(db_session, intent)
    assert len(results) == 2  # Out-of-stock filtered
    assert all(r.category == "headphones" for r in results)


def test_price_filter(db_session):
    intent = AIIntent(category="headphones", max_price_luna=2_000_000)
    results = search_catalog(db_session, intent)
    assert len(results) == 1
    assert results[0].price_luna == 1_500_000


def test_attribute_filter(db_session):
    intent = AIIntent(
        category="headphones",
        attributes={"wireless": True, "noise_cancelling": True},
    )
    results = search_catalog(db_session, intent)
    
    # Should return both in-stock headphones, but Wireless Headphones must be ranked first
    assert len(results) == 2
    assert results[0].name == "Wireless Headphones"
    assert results[0].match_score > results[1].match_score
    
def test_inventory_filter(db_session):
    intent = AIIntent(category="headphones")
    results = search_catalog(db_session, intent)
    assert all(r.availability is True for r in results)
    assert all(r.id != "out-of-stock-id" for r in results)