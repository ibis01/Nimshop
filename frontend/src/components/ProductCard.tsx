import { ProductResult } from "../types";
import { formatNim } from "../utils/format";

interface Props {
  product: ProductResult;
  isBestMatch?: boolean;
  onBuy: (product: ProductResult) => void;
}

const getProductImage = (category: string, name: string) => {
  const c = category.toLowerCase();
  const n = name.toLowerCase();
  if (c.includes("headphone") || n.includes("headphone"))
    return "/products/headphones.svg";
  if (c.includes("keyboard") || n.includes("keyboard"))
    return "/products/keyboard.svg";
  if (c.includes("mouse") || n.includes("mouse")) return "/products/mouse.svg";
  if (c.includes("monitor") || n.includes("monitor"))
    return "/products/monitor.svg";
  return "/products/keyboard.svg"; // Fallback
};

export function ProductCard({ product, isBestMatch, onBuy }: Props) {
  const attributeList = Object.entries(product.attributes || {})
    .filter(([_, v]) => v === true)
    .map(([k]) => k.replace(/_/g, " "));

  const imageSrc = getProductImage(product.category, product.name);

  if (isBestMatch) {
    return (
      <div className="group relative bg-white rounded-3xl border border-orange-200 shadow-lg ring-1 ring-orange-100 mb-6 animate-scale-in overflow-hidden">
        <div className="absolute top-4 left-4 z-10 px-3 py-1.5 bg-orange-500 text-white text-xs font-bold rounded-full shadow-md flex items-center gap-1.5">
          <span className="text-sm">★</span> BEST MATCH
        </div>

        <div className="aspect-[4/3] bg-gray-50 flex items-center justify-center border-b border-gray-100">
          <img
            src={imageSrc}
            alt={product.name}
            className="w-3/4 h-3/4 object-contain"
          />
        </div>

        <div className="p-5">
          <h3 className="font-bold text-xl text-gray-900 leading-tight mb-2">
            {product.name}
          </h3>
          <p className="text-sm text-gray-500 line-clamp-2 mb-4">
            {product.description}
          </p>

          <div className="flex items-baseline gap-3 mb-4">
            <span className="text-3xl font-extrabold text-gray-900">
              {formatNim(product.price_luna)}
            </span>
            <span className="text-xs font-semibold text-orange-600 bg-orange-50 px-2.5 py-1 rounded-lg">
              {Math.round(product.match_score * 100)}% Match
            </span>
          </div>

          {attributeList.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {attributeList.slice(0, 4).map((attr) => (
                <span
                  key={attr}
                  className="px-3 py-1.5 bg-gray-100 text-gray-700 text-xs font-medium rounded-lg"
                >
                  ✓ {attr}
                </span>
              ))}
            </div>
          )}

          <button
            onClick={() => onBuy(product)}
            disabled={!product.availability}
            className="w-full h-12 bg-orange-500 text-white font-bold rounded-xl hover:bg-orange-600 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-md shadow-orange-500/20"
          >
            Buy with NIM
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="group relative bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 mb-3 animate-fade-up overflow-hidden">
      <div className="flex">
        <div className="w-28 h-28 bg-gray-50 flex items-center justify-center border-r border-gray-100 flex-shrink-0">
          <img
            src={imageSrc}
            alt={product.name}
            className="w-20 h-20 object-contain"
          />
        </div>
        <div className="p-4 flex-1 flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-base text-gray-900 leading-tight mb-1 line-clamp-1">
              {product.name}
            </h3>
            <p className="text-xs text-gray-500 line-clamp-2 mb-2">
              {product.description}
            </p>
          </div>

          <div className="flex items-center justify-between mt-auto">
            <span className="text-lg font-bold text-gray-900">
              {formatNim(product.price_luna)}
            </span>
            <button
              onClick={() => onBuy(product)}
              disabled={!product.availability}
              className="h-9 px-4 bg-gray-900 text-white text-sm font-semibold rounded-lg hover:bg-gray-800 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Buy
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
