import { ProductResult } from "../types";
import { ProductCard } from "./ProductCard";

interface Props {
  results: ProductResult[];
  onBuy: (product: ProductResult) => void;
}

export function ProductList({ results, onBuy }: Props) {
  if (results.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">No products found</p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-0">
      {results.map((product, index) => (
        <ProductCard 
          key={product.id} 
          product={product} 
          isBestMatch={index === 0} 
          onBuy={onBuy}
        />
      ))}
    </div>
  );
}
