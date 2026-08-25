import { ProductResult } from "../types";
import { ProductCard } from "./ProductCard";

interface Props {
  results: ProductResult[];
}

export function ProductList({ results }: Props) {
  if (results.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">No products found</p>
        <p className="text-sm mt-1">Try a different search</p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md space-y-3">
      {results.map((product, index) => (
        <ProductCard
          key={product.id}
          product={product}
          isBestMatch={index === 0}
        />
      ))}
    </div>
  );
}