import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)

async def verify_nimiq_transaction(tx_hash: str, recipient: str, amount_luna: int, memo: str, network: str) -> dict:
    """
    Verifies a Nimiq transaction on-chain with strict security checks.
    Returns {"valid": True} or {"valid": False, "reason": "..."}
    """
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransactionByHash",
            "params": [tx_hash]
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(settings.NIMIQ_RPC_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
        if "error" in data:
            return {"valid": False, "reason": f"RPC Error: {data['error'].get('message', 'Unknown error')}"}
            
        tx = data.get("result")
        if not tx:
            return {"valid": False, "reason": "Transaction not found on chain"}
            
        # 1. Check state (must be confirmed)
        if tx.get("state") != "confirmed":
            return {"valid": False, "reason": "Transaction is not confirmed"}
            
        # 2. STRICT NETWORK VALIDATION: mainnet = 1, testnet = 4
        tx_network_id = tx.get("networkId")
        expected_network_id = 4 if network == "testnet" else 1
        if int(tx_network_id) != expected_network_id:
            return {"valid": False, "reason": "Network mismatch"}
            
        # 3. NORMALIZED RECIPIENT COMPARISON
        tx_recipient = tx.get("recipient", {}).get("userFriendlyAddress") or tx.get("recipient", {}).get("address")
        # Normalize: remove spaces, uppercase
        normalized_tx_recipient = str(tx_recipient).replace(" ", "").upper()
        normalized_expected_recipient = str(recipient).replace(" ", "").upper()
        
        if normalized_tx_recipient != normalized_expected_recipient:
            return {"valid": False, "reason": "Recipient mismatch"}
            
        # 4. Check amount
        if tx.get("value") != amount_luna:
            return {"valid": False, "reason": "Amount mismatch"}
            
        # 5. Check memo (data)
        tx_data = tx.get("data")
        if tx_data is None:
            return {"valid": False, "reason": "Missing transaction data"}
            
        # Decode hex data safely
        try:
            hex_str = tx_data[2:] if tx_data.startswith("0x") else tx_data
            decoded_data = bytes.fromhex(hex_str).decode('utf-8')
        except (ValueError, UnicodeDecodeError):
            return {"valid": False, "reason": "Malformed transaction data"}
            
        # STRICT EXACT MATCH for memo (prevents substring attacks)
        if decoded_data != memo:
            return {"valid": False, "reason": "Expected exact match for memo"}
            
        return {"valid": True}
        
    except httpx.RequestError as e:
        logger.error(f"RPC Connection failed: {e}")
        return {"valid": False, "reason": f"RPC connection error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected verification error: {e}")
        return {"valid": False, "reason": "Internal verification error"}
