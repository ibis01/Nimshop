import pytest
from fastapi.testclient import TestClient
from main import app
from models import Product, Seller, Order
from services.payment_service import verify_nimiq_transaction
from unittest.mock import patch
import uuid

# Mock RPC response for testing
MOCK_TX_SUCCESS = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "hash": "mock_tx_hash_123",
        "recipient": {"address": "NQ00 DEMO"},
        "value": 100000,
        "networkId": 4, # Testnet
        "state": "confirmed",
        "data": "0x4e494d53484f503a6f726465725f6964" # Hex for "NIMSHOP:order_id"
    }
}

class MockResponse:
    def raise_for_status(self):
        pass
    def json(self):
        return MOCK_TX_SUCCESS

class MockResponseNone:
    def raise_for_status(self): 
        pass
    def json(self): 
        return {"jsonrpc": "2.0", "id": 1, "result": None}


@pytest.mark.asyncio
async def test_verify_transaction_success():
    with patch("httpx.AsyncClient.post", return_value=MockResponse()):
        result = await verify_nimiq_transaction("mock_tx_hash_123", "NQ00 DEMO", 100000, "NIMSHOP:order_id", "testnet")
        assert result["valid"] is True


@pytest.mark.asyncio
async def test_verify_wrong_amount():
    with patch("httpx.AsyncClient.post", return_value=MockResponse()):
        result = await verify_nimiq_transaction("mock_tx_hash_123", "NQ00 DEMO", 99999, "NIMSHOP:order_id", "testnet")
        assert result["valid"] is False
        assert "Amount mismatch" in result["reason"]


@pytest.mark.asyncio
async def test_verify_unknown_txhash():
    with patch("httpx.AsyncClient.post", return_value=MockResponseNone()):
        result = await verify_nimiq_transaction("unknown_hash", "NQ00 DEMO", 100000, "memo", "testnet")
        assert result["valid"] is False
        assert "not found" in result["reason"]


def test_reused_tx_hash(client: TestClient, db_session):
    """CRITICAL 2: Prevent transaction replay"""
    seller = Seller(id=uuid.uuid4(), name="Test", nimiq_address="NQ00", is_active=True)
    db_session.add(seller)
    db_session.commit()
    
    product = Product(
        name="Test", description="Desc", category="test", 
        price_luna=100000, seller_id=seller.id, inventory_quantity=10
    )
    db_session.add(product)
    db_session.commit()
    
    # Create order 1
    res1 = client.post("/api/orders", json={"product_id": str(product.id), "quantity": 1})
    order_id_1 = res1.json()["order_id"]
    
    # Mock successful verification for order 1 so it saves the tx_hash
    with patch("main.verify_nimiq_transaction", return_value={"valid": True, "reason": "Verified"}):
        res_verify_1 = client.post("/api/orders/verify", json={"order_id": order_id_1, "tx_hash": "reused_hash_123"})
        assert res_verify_1.status_code == 200
        
    # Create second order
    res2 = client.post("/api/orders", json={"product_id": str(product.id), "quantity": 1})
    order_id_2 = res2.json()["order_id"]
    
    # Try to reuse tx_hash on order 2
    with patch("main.verify_nimiq_transaction", return_value={"valid": True, "reason": "Verified"}):
        res_verify_2 = client.post("/api/orders/verify", json={"order_id": order_id_2, "tx_hash": "reused_hash_123"})
        assert res_verify_2.status_code == 409
        assert "already used" in res_verify_2.json()["detail"]


def test_concurrent_inventory_orders(client: TestClient, db_session):
    """CRITICAL 3: Prevent inventory race conditions"""
    seller = Seller(id=uuid.uuid4(), name="Test", nimiq_address="NQ00", is_active=True)
    db_session.add(seller)
    db_session.commit()
    
    # Only 1 item in stock
    product = Product(
        name="Test", description="Desc", category="test", 
        price_luna=100000, seller_id=seller.id, inventory_quantity=1
    )
    db_session.add(product)
    db_session.commit()
    
    # Send 5 rapid requests
    def make_order():
        return client.post("/api/orders", json={"product_id": str(product.id), "quantity": 1})
        
    results = [make_order() for _ in range(5)]
    
    success_count = sum(1 for r in results if r.status_code == 200)
    fail_count = sum(1 for r in results if r.status_code == 400)
    
    assert success_count == 1
    assert fail_count == 4
    
    # Verify inventory is exactly 0
    db_session.refresh(product)
    assert product.inventory_quantity == 0


def test_invalid_quantity(client: TestClient, db_session):
    seller = Seller(id=uuid.uuid4(), name="Test", nimiq_address="NQ00", is_active=True)
    db_session.add(seller)
    db_session.commit()
    
    product = Product(
        name="Test", description="Desc", category="test", 
        price_luna=100000, seller_id=seller.id, inventory_quantity=10
    )
    db_session.add(product)
    db_session.commit()
    
    # Pydantic validates quantity >= 1, so both -1 and 0 return 422 Unprocessable Entity
    res_neg = client.post("/api/orders", json={"product_id": str(product.id), "quantity": -1})
    assert res_neg.status_code == 422 
    
    res_zero = client.post("/api/orders", json={"product_id": str(product.id), "quantity": 0})
    assert res_zero.status_code == 422 