import { useState } from "react";
import { SearchBar } from "./components/SearchBar";
import { ProductList } from "./components/ProductList";
import { StatusMessage } from "./components/StatusMessage";
import { CheckoutModal } from "./components/CheckoutModal";
import { searchProducts, createOrder } from "./api";
import { ProductResult, OrderIntent } from "./types";

function App() {
  const [results, setResults] = useState<ProductResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [checkoutIntent, setCheckoutIntent] = useState<OrderIntent | null>(
    null,
  );

  const handleSearch = async (query: string) => {
    // ... (keep existing search logic) ...
    setIsLoading(true);
    setError(null);
    setHasSearched(true);
    try {
      const response = await searchProducts(query);
      setResults(response.results);
    } catch (err: any) {
      setError(err.message || "Search failed");
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBuy = async (product: ProductResult) => {
    try {
      const intent = await createOrder(product.id, 1);
      setCheckoutIntent(intent);
    } catch (err: any) {
      setError(err.message || "Failed to create order");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-4">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-2">
          NimShop
        </h1>
        <p className="text-center text-gray-600 mb-6">
          AI-powered product discovery with native NIM payments
        </p>

        <div className="flex justify-center mb-6">
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {isLoading && (
          <StatusMessage type="loading" message="Searching catalog..." />
        )}
        {error && <StatusMessage type="error" message={error} />}
        {!isLoading && !error && hasSearched && results.length === 0 && (
          <StatusMessage
            type="empty"
            message="No products matched your search"
          />
        )}

        {!isLoading && results.length > 0 && (
          <ProductList results={results} onBuy={handleBuy} />
        )}
      </div>

      {checkoutIntent && (
        <CheckoutModal
          intent={checkoutIntent}
          onClose={() => setCheckoutIntent(null)}
          onSuccess={() => {
            setCheckoutIntent(null);
            setError(null);
            // In a real app, we'd refresh the cart or show a success page
            alert("Order placed successfully!");
          }}
        />
      )}
    </div>
  );
}

export default App;
