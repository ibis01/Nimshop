import { init } from "@nimiq/mini-app-sdk";

// ... (keep existing checkNimiqProvider) ...

export interface TransactionResult {
  txHash: string;
}

export const sendNimPayment = async (
  recipient: string,
  amountLuna: number,
  data: string,
): Promise<TransactionResult> => {
  try {
    const nimiq = await init();

    // Official SDK method for sending NIM with data/memo.
    // In the current SDK typings, this method expects a single options object.
    const txHash = await (nimiq as any).sendBasicTransactionWithData({
      recipient,
      amount: amountLuna,
      data,
    });

    return { txHash };
  } catch (err: any) {
    throw new Error(err.message || "Payment failed or was rejected");
  }
};
