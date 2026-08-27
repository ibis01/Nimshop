import { SearchResponse, OrderIntent, OrderStatus } from "./types";

const API_BASE = "http://localhost:8000";

export async function searchProducts(query: string): Promise<SearchResponse> {
  const res = await fetch(`${API_BASE}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Search failed" }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

export async function createOrder(
  productId: string,
  quantity: number,
): Promise<OrderIntent> {
  const response = await fetch(`${API_BASE}/api/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ product_id: productId, quantity }),
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Order creation failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export async function verifyOrder(
  orderId: string,
  txHash: string,
): Promise<OrderStatus> {
  const response = await fetch(`${API_BASE}/api/orders/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ order_id: orderId, tx_hash: txHash }),
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Verification failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
