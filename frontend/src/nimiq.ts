import { init } from "@nimiq/mini-app-sdk";

let nimiqProvider: any = null;

async function getNimiqProvider() {
  if (!nimiqProvider) {
    // Official SDK helper to wait until Nimiq Pay injects the provider
    nimiqProvider = await init();
  }
  return nimiqProvider;
}

export async function sendNimPayment(
  recipient: string,
  amountLuna: number,
  memo: string,
): Promise<{ txHash: string }> {
  try {
    const nimiq = await getNimiqProvider();

    // Official Nimiq Mini App SDK method for sending a NIM payment with attached text data (memo)
    const txHash = await nimiq.sendBasicTransactionWithData({
      recipient,
      value: amountLuna,
      data: memo,
    });

    if (!txHash) {
      throw new Error("Payment failed: No transaction hash returned");
    }

    return { txHash };
  } catch (error: any) {
    // Handle user rejection explicitly based on official SDK error types
    if (
      error.name === "PermissionDeniedError" ||
      error.message?.includes("rejected") ||
      error.message?.includes("cancelled")
    ) {
      throw new Error("Payment was cancelled by user");
    }
    throw new Error(error.message || "Payment failed");
  }
}
