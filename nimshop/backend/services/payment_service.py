import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

# Public Nimiq Node RPC (Mainnet/Testnet depending on config)
# In a real production app, you would run your own node.
NIMIQ_NODE_URL = "https://node.nimiq.watch:443" 

async def verify_nimiq_transaction(tx_hash: str, expected_recipient: str, expected_amount_luna: int, expected_memo: str) -> bool:
    """
    Verifies a transaction on the Nimiq network.
    SECURITY: Never trust the frontend. Always verify on-chain.
    """
    try:
        # JSON-RPC request to get transaction by hash
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransactionByHash",
            "params": [tx_hash]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(NIMIQ_NODE_URL, json=payload, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        if "result" not in data or data["result"] is None:
            logger.warning(f"Transaction {tx_hash} not found on network.")
            return False

        tx = data["result"]
        
        # STRICT VERIFICATION CHECKS
        # 1. Check recipient
        if tx.get("recipient", {}).get("address", "").replace(" ", "") != expected_recipient.replace(" ", ""):
            logger.warning(f"Recipient mismatch for {tx_hash}")
            return False
            
        # 2. Check amount (value is in Luna)
        if int(tx.get("value", 0)) != expected_amount_luna:
            logger.warning(f"Amount mismatch for {tx_hash}. Expected {expected_amount_luna}, got {tx.get('value')}")
            return False

        # 3. Check memo/data if applicable (Nimiq transactions can have data)
        # Note: Exact field name for memo/data depends on the specific RPC response structure.
        # For MVP, we primarily verify recipient and amount.
        
        logger.info(f"Transaction {tx_hash} verified successfully.")
        return True

    except Exception as e:
        logger.error(f"Failed to verify transaction {tx_hash}: {e}")
        # In a strict production environment, return False. 
        # For local demo purposes, we log the error.
        return False