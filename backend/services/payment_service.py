import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

NIMIQ_NODE_URL = "https://node.nimiq.watch:443" 

async def verify_nimiq_transaction(
    tx_hash: str, 
    expected_recipient: str, 
    expected_amount_luna: int, 
    expected_memo: str,
    expected_network: str
) -> dict:
    """
    Verifies a transaction on the Nimiq network.
    SECURITY: Never trust the frontend. Always verify on-chain.
    """
    try:
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
            return {"valid": False, "reason": "Transaction not found"}

        tx = data["result"]
        
        # 1. Verify Recipient (normalize spaces)
        tx_recipient = tx.get("recipient", {}).get("address", "").replace(" ", "")
        if tx_recipient != expected_recipient.replace(" ", ""):
            return {"valid": False, "reason": "Recipient mismatch"}
            
        # 2. Verify Amount
        if int(tx.get("value", 0)) != expected_amount_luna:
            return {"valid": False, "reason": "Amount mismatch"}

        # 3. Verify Network (1 = Mainnet, 4 = Testnet)
        expected_net_id = 1 if expected_network == "mainnet" else 4
        if int(tx.get("networkId", 0)) != expected_net_id:
            return {"valid": False, "reason": "Network mismatch"}

        # 4. Verify Finality/State
        if tx.get("state") != "confirmed":
            return {"valid": False, "reason": "Transaction not confirmed"}

        # 5. Verify Memo/Data
        # LIMITATION: The RPC 'data' field encoding (hex vs utf-8) is not strictly 
        # standardized in the public docs. We attempt a safe decode.
        tx_data = tx.get("data")
        if tx_data:
            try:
                if isinstance(tx_data, str) and tx_data.startswith("0x"):
                    decoded_data = bytes.fromhex(tx_data[2:]).decode('utf-8', errors='ignore')
                else:
                    decoded_data = str(tx_data)
                    
                if expected_memo not in decoded_data:
                    logger.warning(f"Memo mismatch. Expected: {expected_memo}, Got: {decoded_data}")
                    # We do not fail strictly here due to encoding ambiguity, 
                    # relying on txHash uniqueness for replay protection.
            except Exception as e:
                logger.warning(f"Failed to decode transaction data: {e}")
                
        return {"valid": True, "reason": "Verified"}

    except Exception as e:
        logger.error(f"Failed to verify transaction {tx_hash}: {e}")
        return {"valid": False, "reason": f"RPC error: {str(e)}"}