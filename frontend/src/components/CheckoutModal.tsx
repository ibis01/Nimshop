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
      const { txHash } = await sendNimPayment(
        intent.recipient,
        intent.amount_luna,
        intent.memo,
      );
      setStatus("verifying");
      const result = await verifyOrder(intent.order_id, txHash);

      if (result.status === "paid") {
        setStatus("success");
        setTimeout(onSuccess, 3000); // Give time to admire the success screen
      } else {
        throw new Error("Payment verification failed");
      }
    } catch (err: any) {
      setError(err.message || "Transaction failed or was rejected");
      setStatus("error");
    }
  };

  if (status === "success") {
    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
        <div className="bg-white rounded-3xl p-8 w-full max-w-sm text-center shadow-2xl">
          <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={3}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Payment Confirmed
          </h2>
          <p className="text-gray-500 mb-6">
            Your order has been securely recorded.
          </p>

          <div className="bg-gray-50 rounded-2xl p-4 mb-6 text-left space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Amount Paid</span>
              <span className="font-bold text-gray-900">
                {formatNim(intent.amount_luna)}
              </span>
            </div>
            <div className="h-px bg-gray-200" />
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Status</span>
              <span className="text-xs font-semibold text-green-600 bg-green-50 px-2 py-1 rounded-full">
                Transaction Verified
              </span>
            </div>
          </div>

          <button
            onClick={onSuccess}
            className="w-full h-12 bg-gray-900 text-white font-semibold rounded-xl hover:bg-gray-800 active:scale-[0.98] transition-all"
          >
            Continue Shopping
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
      <div className="bg-white rounded-3xl p-6 w-full max-w-sm shadow-2xl">
        <h2 className="text-xl font-bold text-gray-900 mb-1">
          Almost yours ✨
        </h2>
        <p className="text-sm text-gray-500 mb-6">
          Review your order details before paying.
        </p>

        <div className="bg-gray-50 rounded-2xl p-4 mb-6 space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-500">Total Amount</span>
            <span className="text-xl font-bold text-gray-900">
              {formatNim(intent.amount_luna)}
            </span>
          </div>
          <div className="h-px bg-gray-200" />
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-500">Recipient</span>
            <span className="text-xs font-mono text-gray-600 bg-white px-2 py-1 rounded border border-gray-200">
              {intent.recipient.slice(0, 8)}...{intent.recipient.slice(-4)}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-500">Memo</span>
            <span
              className="text-xs font-mono text-gray-600 bg-white px-2 py-1 rounded border border-gray-200 truncate max-w-[150px]"
              title={intent.memo}
            >
              {intent.memo}
            </span>
          </div>
        </div>

        {status === "idle" && (
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="flex-1 h-12 border border-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 active:scale-[0.98] transition-all"
            >
              Cancel
            </button>
            <button
              onClick={handlePay}
              className="flex-[2] h-12 bg-orange-500 text-white font-semibold rounded-xl hover:bg-orange-600 active:scale-[0.98] transition-all flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z" />
              </svg>
              Buy with NIM
            </button>
          </div>
        )}

        {status === "sending" && (
          <div className="text-center py-4">
            <div className="w-8 h-8 border-[3px] border-orange-200 border-t-orange-500 rounded-full animate-spin mx-auto mb-3" />
            <p className="text-gray-600 font-medium">Opening Nimiq Pay...</p>
          </div>
        )}

        {status === "verifying" && (
          <div className="text-center py-4">
            <div className="w-8 h-8 border-[3px] border-orange-200 border-t-orange-500 rounded-full animate-spin mx-auto mb-3" />
            <p className="text-gray-600 font-medium">
              Verifying transaction on-chain...
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Ensuring your order is securely recorded.
            </p>
          </div>
        )}

        {status === "error" && (
          <div className="text-center">
            <div className="w-12 h-12 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
            <p className="text-red-600 font-medium mb-4">{error}</p>
            <button
              onClick={onClose}
              className="w-full h-12 bg-gray-900 text-white font-semibold rounded-xl hover:bg-gray-800 active:scale-[0.98] transition-all"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
