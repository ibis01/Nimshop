export interface SellerSummary {
  id: string;
  name: string;
}

export interface ProductResult {
  id: string;
  name: string;
  description: string;
  price_luna: number;
  category: string;
  attributes: Record<string, any>;
  seller: SellerSummary;
  availability: boolean;
  match_score: number;
}

export interface SearchResponse {
  query: string;
  results: ProductResult[];
  intent?: {
    category?: string;
    max_price_luna?: number;
    attributes?: Record<string, any>;
  };
  used_fallback: boolean;
}

export interface OrderIntent {
  order_id: string;
  recipient: string;
  amount_luna: number;
  memo: string;
}

export interface OrderStatus {
  order_id: string;
  status: string;
  tx_hash?: string;
}
