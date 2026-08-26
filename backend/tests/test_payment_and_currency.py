import pytest
from fastapi.testclient import TestClient
from main import app
from models import Product, Seller, Order
from services.payment_service import verify_nimiq_transaction
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
import uuid

class MockResponse:
    def __init__(self, json_data):
        self._json_data = json_data
    def raise_for_status(self): pass
    def json(self): return self._json_data

def make_mock_post(json_data):
    async def mock_post(*args, **kwargs):
        return MockResponse(json_data)
    return mock_post

# Factory function ensures a fresh, independent dictionary for every test
def get_mock_tx_success():
    return {
        "jsonrpc": "2.0", "id": 1,
        "result": {
            "hash": "mock_tx_hash_123",
            "recipient": {"address": "NQ00 DEMO", "userFriendlyAddress": "NQ00 DEMO"},
            "value": 100000, "networkId": 4, "state": "confirmed",
            "data": "0x4e494d53484f503a746573745f6f72646572" # "NIMSHOP:test_order"
        }
    }

@pytest.mark.asyncio
async def test_verify_correct_memo():
    with patch("httpx.AsyncClient.post", side_effect=make_mock_post(get_mock_tx_success())):
        result = await verify_nimiq_transaction("mock_tx_hash_123", "NQ00 DEMO", 100000, "NIMSHOP:test_order", "testnet")
        assert result["valid"] is True

@pytest.mark.asyncio
async def test_verify_incorrect_memo():
    mock_data = get_mock_tx_success()
    with patch("httpx.AsyncClient.post", side_effect=make_mock_post(mock_data)):
        result = await verify_nimiq_transaction("mock_tx_hash_123", "NQ00 DEMO", 100000, "WRONG_MEMO", "testnet")
        assert result["valid"] is False and "Expected exact match" in result["reason"]

@pytest.mark.asyncio
async def test_verify_missing_memo():
    mock_data = get_mock_tx_success()
    del mock_data["result"]["data"]
    with patch("httpx.AsyncClient.post", side_effect=make_mock_post(mock_data)):
        result = await verify_nimiq_transaction("mock_tx_hash_123", "NQ00 DEMO", 100000, "NIMSHOP:test_order", "testnet")
        assert result["valid"] is False and "Missing transaction data" in result["reason"]

@pytest.mark.asyncio
async def test_verify_malformed_data():
    mock_data = get_mock_tx_success()
    mock_data["result"]["data"] = "0xNOTVALIDHEX"
    with patch("httpx.AsyncClient.post", side_effect=make_mock_post(mock_data)):
        result = await verify_nimiq_transaction("mock_tx_hash_123", "NQ00 DEMO", 100000, "NIMSHOP:test_order", "testnet")
        assert result["valid"] is False and "Malformed transaction data" in result["reason"]

@pytest.mark.asyncio
async def test_verify_wrong_network():
    mock_data = get_mock_tx_success()
    mock_data["result"]["networkId"] = 1
    with patch("httpx.AsyncClient.post", side_effect=make_mock_post(mock_data)):
        result = await verify_nimiq_transaction("mock_tx_hash_123", "NQ00 DEMO", 100000, "NIMSHOP:test_order", "testnet")
        assert result["valid"] is False and "Network mismatch" in result["reason"]

@pytest.mark.asyncio
async def test_verify_wrong_state():
    mock_data = get_mock_tx_success()
    mock_data["result"]["state"] = "pending"
    with patch("httpx.AsyncClient.post", side_effect=make_mock_post(mock_data)):
        result = await verify_nimiq_transaction("mock_tx_hash_123", "NQ00 DEMO", 100000, "NIMSHOP:test_order", "testnet")
        assert result["valid"] is False and "not confirmed" in result["reason"]

@pytest.mark.asyncio
async def test_verify_wrong_recipient():
    mock_data = get_mock_tx_success()
    mock_data["result"]["recipient"]["address"] = "NQ99 WRONG"
    mock_data["result"]["recipient"]["userFriendlyAddress"] = "NQ99 WRONG"
    with patch("httpx.AsyncClient.post", side_effect=make_mock_post(mock_data)):
        result = await verify_nimiq_transaction("mock_tx_hash_123", "NQ00 DEMO", 100000, "NIMSHOP:test_order", "testnet")
        assert result["valid"] is False and "Recipient mismatch" in result["reason"]

@pytest.mark.asyncio
async def test_verify_wrong_amount():
    mock_data = get_mock_tx_success()
    with patch("httpx.AsyncClient.post", side_effect=make_mock_post(mock_data)):
        result = await verify_nimiq_transaction("mock_tx_hash_123", "NQ00 DEMO", 99999, "NIMSHOP:test_order", "testnet")
        assert result["valid"] is False and "Amount mismatch" in result["reason"]

@pytest.mark.asyncio
async def test_verify_memo_is_substring_but_not_exact():
    """Security test: Ensure attacker cannot append data to a valid memo."""
    mock_data = get_mock_tx_success()
    # Hex for "NIMSHOP:test_order-ATTACKER-DATA"
    mock_data["result"]["data"] = "0x4e494d53484f503a746573745f6f726465722d41545441434b45522d44415441"
    with patch("httpx.AsyncClient.post", side_effect=make_mock_post(mock_data)):
        result = await verify_nimiq_transaction("mock_tx_hash_123", "NQ00 DEMO", 100000, "NIMSHOP:test_order", "testnet")
        assert result["valid"] is False and "Expected exact match" in result["reason"]

def test_reused_tx_hash(client: TestClient, db_session):
    seller = Seller(id=uuid.uuid4(), name="Test", nimiq_address="NQ00", is_active=True)
    db_session.add(seller); db_session.commit()
    product = Product(name="Test", description="Desc", category="test", price_luna=100000, seller_id=seller.id, inventory_quantity=10)
    db_session.add(product); db_session.commit()
    
    res1 = client.post("/api/orders", json={"product_id": str(product.id), "quantity": 1})
    order_id_1 = res1.json()["order_id"]
    
    with patch("main.verify_nimiq_transaction", return_value={"valid": True, "reason": "Verified"}):
        assert client.post("/api/orders/verify", json={"order_id": order_id_1, "tx_hash": "reused_hash_123"}).status_code == 200
        
    res2 = client.post("/api/orders", json={"product_id": str(product.id), "quantity": 1})
    order_id_2 = res2.json()["order_id"]
    
    with patch("main.verify_nimiq_transaction", return_value={"valid": True, "reason": "Verified"}):
        res_verify_2 = client.post("/api/orders/verify", json={"order_id": order_id_2, "tx_hash": "reused_hash_123"})
        assert res_verify_2.status_code == 409 and "already used" in res_verify_2.json()["detail"]

def test_expired_reservation_and_inventory_restoration(client: TestClient, db_session):
    seller = Seller(id=uuid.uuid4(), name="Test", nimiq_address="NQ00", is_active=True)
    db_session.add(seller); db_session.commit()
    product = Product(name="Test", description="Desc", category="test", price_luna=100000, seller_id=seller.id, inventory_quantity=1)
    db_session.add(product); db_session.commit()
    
    res1 = client.post("/api/orders", json={"product_id": str(product.id), "quantity": 1})
    order_id_str = res1.json()["order_id"]
    
    order = db_session.query(Order).filter(Order.id == uuid.UUID(order_id_str)).first()
    order.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
    db_session.commit()
    
    with patch("main.verify_nimiq_transaction", return_value={"valid": True, "reason": "Verified"}):
        res_verify = client.post("/api/orders/verify", json={"order_id": order_id_str, "tx_hash": "some_hash"})
        assert res_verify.status_code == 400 and "expired" in res_verify.json()["detail"].lower()
        
    db_session.refresh(product)
    assert product.inventory_quantity == 1 # Restored
    db_session.refresh(order)
    assert order.status == "cancelled"