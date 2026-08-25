import { ProductResult } from "../types";
import { formatNim } from "../utils/format";

interface Props {
  product: ProductResult;
  isBestMatch?: boolean;
  onBuy: (product: ProductResult) => void;
}

export function ProductCard({ product, isBestMatch, onBuy }: Props) {
  // ... (keep existing attribute and seller display) ...
  const attributeList = Object.entries(product.attributes || {})
    .filter(([_, v]) => v === true)
    .map(([k]) => k.replace(/_/g, " "));

  return (
    <div
      className={`p-4 bg-white rounded-lg shadow-sm border ${isBestMatch ? "border-blue-500 ring-2 ring-blue-200" : "border-gray-200"}`}
    >
      {isBestMatch && (
        <div className="text-xs font-semibold text-blue-600 mb-2">
          ⭐ BEST MATCH
        </div>
      )}
      <h3 className="font-bold text-lg text-gray-900">{product.name}</h3>
      <p className="text-sm text-gray-600 mt-1">{product.description}</p>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold text-gray-900">
          {formatNim(product.price_luna)}
        </span>
        <span className="text-xs text-gray-500">
          Match: {(product.match_score * 100).toFixed(0)}%
        </span>
      </div>

      {attributeList.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
          {attributeList.map((attr) => (
            <span
              key={attr}
              className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
            >
              ✓ {attr}
            </span>
          ))}
        </div>
      )}

      <div className="mt-3 flex justify-between items-center text-sm">
        <span className="text-gray-600">Seller: {product.seller.name}</span>
        <span
          className={product.availability ? "text-green-600" : "text-red-600"}
        >
          {product.availability ? "In Stock" : "Out of Stock"}
        </span>
      </div>

      {product.availability && (
        <button
          onClick={() => onBuy(product)}
          className="mt-4 w-full py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Buy Now
        </button>
      )}
    </div>
  );
}
