import logging
import httpx
from config import settings

logger = logging.getLogger(__name__)

async def verify_nimiq_transaction(
    tx_hash: str, 
    expected_recipient: str, 
    expected_amount_luna: int, 
    expected_memo: str,
    expected_network: str
) -> dict:
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransactionByHash",
            "params": [tx_hash]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(settings.nimiq_rpc_url, json=payload, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        if "result" not in data or data["result"] is None:
            return {"valid": False, "reason": "Transaction not found"}

        tx = data["result"]
        
        # 1. Verify Recipient (robust extraction)
        recipient_data = tx.get("recipient", {})
        if isinstance(recipient_data, dict):
            tx_recipient = recipient_data.get("userFriendlyAddress", "") or recipient_data.get("address", "")
        else:
            tx_recipient = str(recipient_data)
            
        if tx_recipient.replace(" ", "").upper() != expected_recipient.replace(" ", "").upper():
            return {"valid": False, "reason": f"Recipient mismatch: expected '{expected_recipient}', got '{tx_recipient}'"}
            
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

        # 5. STRICT Memo Verification
        tx_data = tx.get("data")
        if not tx_data:
            return {"valid": False, "reason": "Missing transaction data/memo"}
            
        try:
            if isinstance(tx_data, str) and tx_data.startswith("0x"):
                decoded_data = bytes.fromhex(tx_data[2:]).decode('utf-8', errors='strict')
            else:
                decoded_data = str(tx_data)
                
            if expected_memo not in decoded_data:
                return {"valid": False, "reason": f"Memo mismatch. Expected: '{expected_memo}', Got: '{decoded_data}'"}
        except ValueError as e:
            return {"valid": False, "reason": f"Malformed transaction data (hex decode failed): {e}"}
        except UnicodeDecodeError as e:
            return {"valid": False, "reason": f"Malformed transaction data (utf-8 decode failed): {e}"}
                
        return {"valid": True, "reason": "Verified"}

    except Exception as e:
        logger.error(f"Failed to verify transaction {tx_hash}: {e}")
        return {"valid": False, "reason": f"RPC error: {str(e)}"}