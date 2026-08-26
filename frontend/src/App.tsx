import { useState, useEffect } from "react";
import { SearchBar } from "./components/SearchBar";
import { ProductList } from "./components/ProductList";
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
    const url = new URL(window.location.href);
    url.searchParams.set("search", query);
    window.history.replaceState({}, "", url.toString());

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

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const initialQuery = params.get("search");
    if (initialQuery && initialQuery.trim().length > 0) {
      handleSearch(initialQuery.trim());
    }
  }, []);

  const handleBuy = async (product: ProductResult) => {
    try {
      const intent = await createOrder(product.id, 1);
      setCheckoutIntent(intent);
    } catch (err: any) {
      setError(err.message || "Failed to create order");
    }
  };

  const handleCheckoutSuccess = () => {
    setCheckoutIntent(null);
    setError(null);
    setResults([]);
    setHasSearched(false);
    const url = new URL(window.location.href);
    url.searchParams.delete("search");
    window.history.replaceState({}, "", url.toString());
  };

  return (
    <div className="min-h-screen bg-[#FAFAF8] flex flex-col">
      <div className="w-full max-w-md mx-auto p-4 flex flex-col min-h-screen">
        <div className="pt-8 pb-6 text-center">
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight mb-2">
            Nim<span className="text-orange-500">Shop</span>
          </h1>
          <p className="text-gray-500 text-sm">
            {hasSearched
              ? "AI-powered product discovery"
              : "Your AI shopping assistant"}
          </p>
        </div>

        <div className="mb-8">
          <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {isLoading && (
          <div className="flex-1 flex flex-col items-center justify-center text-center animate-fade-in">
            <div className="w-10 h-10 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin mb-4" />
            <p className="text-gray-900 font-semibold text-lg">
              Understanding your request
            </p>
            <p className="text-gray-500 text-sm mt-1">
              Finding the best matches for you...
            </p>
          </div>
        )}

        {error && !isLoading && (
          <div className="flex-1 flex flex-col items-center justify-center text-center animate-fade-in">
            <div className="w-12 h-12 bg-red-50 text-red-500 rounded-full flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <p className="text-gray-900 font-semibold mb-1">
              Something went wrong
            </p>
            <p className="text-gray-500 text-sm">{error}</p>
          </div>
        )}

        {!isLoading && !error && hasSearched && results.length === 0 && (
          <div className="flex-1 flex flex-col items-center justify-center text-center animate-fade-in">
            <div className="w-12 h-12 bg-gray-100 text-gray-400 rounded-full flex items-center justify-center mb-4">
              <svg
                className="w-6 h-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <p className="text-gray-900 font-semibold mb-1">No matches found</p>
            <p className="text-gray-500 text-sm">
              Try adjusting your search terms
            </p>
          </div>
        )}

        {!isLoading && results.length > 0 && (
          <div className="flex-1 animate-fade-in">
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-gray-500 font-medium">
                Found {results.length} match{results.length !== 1 ? "es" : ""}
              </p>
            </div>
            <ProductList results={results} onBuy={handleBuy} />
          </div>
        )}
      </div>

      {checkoutIntent && (
        <CheckoutModal
          intent={checkoutIntent}
          onClose={() => setCheckoutIntent(null)}
          onSuccess={handleCheckoutSuccess}
        />
      )}
    </div>
  );
}

export default App;
