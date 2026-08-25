import pytest


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_search_valid(client, db_session):
    # Seed minimal data
    from models import Seller, Product
    import uuid
    seller = Seller(id=uuid.uuid4(), name="Test", nimiq_address="NQ00", is_active=True)
    db_session.add(seller)
    db_session.commit()
    product = Product(
        name="Test Headphones",
        description="Test",
        category="headphones",
        price_luna=1_000_000,
        seller_id=seller.id,
        inventory_quantity=5,
        attributes={"wireless": True},
    )
    db_session.add(product)
    db_session.commit()

    response = client.post("/api/search", json={"query": "wireless headphones"})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "intent" in data


def test_search_empty_query(client):
    response = client.post("/api/search", json={"query": ""})
    assert response.status_code == 422


def test_search_too_long_query(client):
    response = client.post("/api/search", json={"query": "a" * 1000})
    assert response.status_code == 422


def test_search_sql_injection(client):
    response = client.post("/api/search", json={"query": "'; DROP TABLE products; --"})
    assert response.status_code == 200  # Safely handled, no error
    data = response.json()
    assert data["results"] == [] or isinstance(data["results"], list)