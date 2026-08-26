import { useState } from "react";

interface Props {
  onSearch: (query: string) => void;
  isLoading: boolean;
  isHero?: boolean;
}

const EXAMPLES = [
  { label: "🎧 Headphones", query: "wireless headphones" },
  { label: " Work setup", query: "mechanical keyboard" },
  { label: "🎮 Gaming", query: "gaming mouse" },
  { label: "🏠 Home", query: "smart monitor" },
];

export function SearchBar({ onSearch, isLoading, isHero }: Props) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  };

  return (
    <div className="w-full space-y-4 animate-scale-in">
      {isHero && (
        <div className="text-center px-4 mb-2">
          <p className="text-2xl font-bold text-gray-900 leading-tight">
            Tell me what you're looking for.
          </p>
          <p className="text-gray-500 mt-2">I'll find the best match.</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="relative group">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={
            isHero
              ? "e.g., wireless headphones under 50 NIM"
              : "Search products..."
          }
          disabled={isLoading}
          className={`w-full bg-white border border-gray-200 rounded-2xl shadow-sm focus:outline-none focus:ring-4 focus:ring-orange-500/10 focus:border-orange-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed placeholder:text-gray-400 text-gray-900 ${
            isHero ? "h-14 pl-12 pr-28 text-base" : "h-12 pl-10 pr-24 text-sm"
          }`}
        />
        <svg
          className={`absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 ${isHero ? "w-5 h-5" : "w-4 h-4"}`}
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
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className={`absolute right-2 top-1/2 -translate-y-1/2 bg-gray-900 text-white font-semibold rounded-xl hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 active:scale-95 ${
            isHero ? "h-10 px-5" : "h-8 px-4 text-xs"
          }`}
        >
          {isLoading ? (
            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            "Search"
          )}
        </button>
      </form>

      {isHero && (
        <div className="flex flex-wrap gap-2 justify-center px-2">
          {EXAMPLES.map((ex) => (
            <button
              key={ex.query}
              onClick={() => onSearch(ex.query)}
              disabled={isLoading}
              className="px-4 py-2.5 bg-white border border-gray-200 rounded-full text-sm font-medium text-gray-700 hover:border-orange-300 hover:text-orange-600 hover:bg-orange-50 hover:shadow-sm transition-all disabled:opacity-50 active:scale-95 min-h-[44px]"
            >
              {ex.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
