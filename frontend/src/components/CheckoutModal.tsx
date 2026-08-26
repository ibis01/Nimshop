import { useState } from "react";
import { OrderIntent } from "../types";
import { sendNimPayment } from "../nimiq";
import { verifyOrder } from "../api";
import { formatNim } from "../utils/format";

interface Props {
  intent: OrderIntent;
  onClose: () => void;
  onSuccess: () => void;
}

export function CheckoutModal({ intent, onClose, onSuccess }: Props) {
  const [status, setStatus] = useState<
    "idle" | "sending" | "verifying" | "success" | "error"
  >("idle");
  const [error, setError] = useState<string | null>(null);

  const handlePay = async () => {
    setStatus("sending");
    setError(null);
    try {
      // 1. Invoke Nimiq Pay
      const { txHash } = await sendNimPayment(
        intent.recipient,
        intent.amount_luna,
        intent.memo,
      );

      // 2. Verify on backend
      setStatus("verifying");
      const result = await verifyOrder(intent.order_id, txHash);

      if (result.status === "paid") {
        setStatus("success");
        setTimeout(onSuccess, 2000);
      } else {
        throw new Error("Payment verification failed");
      }
    } catch (err: any) {
      setError(err.message || "Transaction failed");
      setStatus("error");
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-sm">
        <h2 className="text-xl font-bold mb-4">Confirm Payment</h2>

        <div className="space-y-2 mb-6 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Amount:</span>
            <span className="font-bold">{formatNim(intent.amount_luna)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Recipient:</span>
            <span className="font-mono text-xs">
              {intent.recipient.substring(0, 12)}...
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Memo:</span>
            <span className="font-mono text-xs">{intent.memo}</span>
          </div>
        </div>

        {status === "idle" && (
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="flex-1 py-2 border border-gray-300 rounded-lg"
            >
              Cancel
            </button>
            <button
              onClick={handlePay}
              className="flex-1 py-2 bg-blue-600 text-white rounded-lg font-semibold"
            >
              Pay with NIM
            </button>
          </div>
        )}

        {status === "sending" && (
          <p className="text-center text-blue-600">Opening Nimiq Pay...</p>
        )}
        {status === "verifying" && (
          <p className="text-center text-blue-600">
            Verifying transaction on-chain...
          </p>
        )}
        {status === "success" && (
          <p className="text-center text-green-600 font-bold">
            ✅ Payment Confirmed!
          </p>
        )}
        {status === "error" && (
          <div>
            <p className="text-center text-red-600 mb-2">{error}</p>
            <button
              onClick={onClose}
              className="w-full py-2 border border-gray-300 rounded-lg"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
