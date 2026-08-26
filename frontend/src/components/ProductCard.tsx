import { ProductResult } from "../types";
import { formatNim } from "../utils/format";

interface Props {
  product: ProductResult;
  isBestMatch?: boolean;
  onBuy: (product: ProductResult) => void;
}

export function ProductCard({ product, isBestMatch, onBuy }: Props) {
  const attributeList = Object.entries(product.attributes || {})
    .filter(([_, v]) => v === true)
    .map(([k]) => k.replace(/_/g, " "));

  return (
    <div
      className={`group relative bg-white rounded-3xl border transition-all duration-300 hover:shadow-lg ${isBestMatch ? "border-orange-200 shadow-md ring-1 ring-orange-100" : "border-gray-100 shadow-sm"}`}
    >
      {isBestMatch && (
        <div className="absolute -top-3 left-4 px-3 py-1 bg-orange-500 text-white text-xs font-bold rounded-full shadow-sm flex items-center gap-1">
          <span>★</span> BEST MATCH
        </div>
      )}

      <div className="p-5">
        <div className="aspect-video bg-gray-50 rounded-2xl mb-4 flex items-center justify-center text-gray-300 border border-gray-100">
          <svg
            className="w-12 h-12"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>

        <h3 className="font-bold text-lg text-gray-900 leading-tight mb-1">
          {product.name}
        </h3>
        <p className="text-sm text-gray-500 line-clamp-2 mb-4">
          {product.description}
        </p>

        <div className="flex items-baseline gap-2 mb-4">
          <span className="text-2xl font-bold text-gray-900">
            {formatNim(product.price_luna)}
          </span>
          {isBestMatch && (
            <span className="text-xs font-medium text-orange-600 bg-orange-50 px-2 py-0.5 rounded-md">
              {Math.round(product.match_score * 100)}% Match
            </span>
          )}
        </div>

        {attributeList.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-5">
            {attributeList.slice(0, 3).map((attr) => (
              <span
                key={attr}
                className="px-2.5 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-lg"
              >
                ✓ {attr}
              </span>
            ))}
          </div>
        )}

        <button
          onClick={() => onBuy(product)}
          disabled={!product.availability}
          className="w-full h-12 bg-gray-900 text-white font-semibold rounded-xl hover:bg-gray-800 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z" />
          </svg>
          Buy with NIM
        </button>
      </div>
    </div>
  );
}
