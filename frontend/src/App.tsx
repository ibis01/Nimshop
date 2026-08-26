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
  const [searchQuery, setSearchQuery] = useState("");

  const executeSearch = async (query: string) => {
    setSearchQuery(query);
    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    const url = new URL(window.location.href);
    url.searchParams.set("search", query);
    window.history.replaceState({}, "", url.toString());

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

  // Clean React pattern: Inline initial fetch to avoid dependency array issues
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const initialQuery = params.get("search");
    if (initialQuery && initialQuery.trim().length > 0) {
      const query = initialQuery.trim();
      setSearchQuery(query);
      setIsLoading(true);
      setError(null);
      setHasSearched(true);

      searchProducts(query)
        .then((response) => setResults(response.results))
        .catch((err: any) => {
          setError(err.message || "Search failed");
          setResults([]);
        })
        .finally(() => setIsLoading(false));
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
    setSearchQuery("");
    const url = new URL(window.location.href);
    url.searchParams.delete("search");
    window.history.replaceState({}, "", url.toString());
  };

  return (
    <div className="min-h-screen bg-[#FAFAF8] flex flex-col">
      <div className="w-full max-w-md mx-auto p-4 flex flex-col min-h-screen">
        {/* Header */}
        <div
          className={`pt-8 pb-6 text-center transition-all duration-500 ${hasSearched ? "pt-4 pb-2" : "pt-12 pb-8"}`}
        >
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight mb-1">
            Nim<span className="text-orange-500">Shop</span>
          </h1>
          <p className="text-gray-500 text-sm font-medium">
            {hasSearched
              ? "AI-powered product discovery"
              : "Shop smarter with NIM"}
          </p>
        </div>

        {/* Search Section */}
        <div
          className={`mb-6 transition-all duration-500 ${hasSearched ? "mb-4" : "mb-8"}`}
        >
          <SearchBar
            onSearch={executeSearch}
            isLoading={isLoading}
            isHero={!hasSearched}
          />
        </div>

        {/* AI Personality & Loading State */}
        {isLoading && (
          <div className="flex-1 flex flex-col items-center justify-center text-center animate-fade-up px-6">
            <div className="relative mb-6">
              <div className="w-12 h-12 border-4 border-orange-100 border-t-orange-500 rounded-full animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center text-orange-500 text-lg">
                ✨
              </div>
            </div>
            <p className="text-gray-900 font-semibold text-lg mb-1">Got it.</p>
            <p className="text-gray-500 text-sm">
              Looking for {searchQuery.toLowerCase()}...
            </p>
          </div>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <div className="flex-1 flex flex-col items-center justify-center text-center animate-fade-up px-6">
            <div className="w-14 h-14 bg-red-50 text-red-500 rounded-2xl flex items-center justify-center mb-4">
              <svg
                className="w-7 h-7"
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

        {/* Empty State */}
        {!isLoading && !error && hasSearched && results.length === 0 && (
          <div className="flex-1 flex flex-col items-center justify-center text-center animate-fade-up px-6">
            <div className="w-14 h-14 bg-gray-100 text-gray-400 rounded-2xl flex items-center justify-center mb-4">
              <svg
                className="w-7 h-7"
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

        {/* Results State */}
        {!isLoading && results.length > 0 && (
          <div className="flex-1 animate-fade-up">
            <div className="mb-5 px-1">
              <p className="text-sm text-gray-500 font-medium mb-1">
                Found {results.length} match{results.length !== 1 ? "es" : ""}
              </p>
              <p className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                🏆 I think you'll like this one.
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
