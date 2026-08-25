import pytest
from models import Seller, Product


def test_create_seller(db_session):
    seller = Seller(name="Test Seller", nimiq_address="NQ00 TEST")
    db_session.add(seller)
    db_session.commit()
    assert seller.id is not None
    assert seller.is_active is True


def test_create_product(db_session):
    seller = Seller(name="Test", nimiq_address="NQ00")
    db_session.add(seller)
    db_session.commit()

    product = Product(
        name="Test Product",
        description="Desc",
        category="test",
        price_luna=100_000,
        seller_id=seller.id,
        inventory_quantity=5,
    )
    db_session.add(product)
    db_session.commit()
    assert product.price_luna == 100_000
    assert product.seller.name == "Test"


def test_price_is_integer(db_session):
    seller = Seller(name="Test", nimiq_address="NQ00")
    db_session.add(seller)
    db_session.commit()

    product = Product(
        name="Test",
        description="Desc",
        category="test",
        price_luna=100_000,  # 1 NIM
        seller_id=seller.id,
        inventory_quantity=1,
    )
    db_session.add(product)
    db_session.commit()
    assert isinstance(product.price_luna, int)