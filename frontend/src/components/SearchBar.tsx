import { useState } from "react";

interface Props {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

const EXAMPLES = [
  "Wireless headphones under 50 NIM",
  "A good keyboard for coding",
  "Gaming accessories under 100 NIM",
];

export function SearchBar({ onSearch, isLoading }: Props) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  };

  return (
    <div className="w-full space-y-4">
      <form onSubmit={handleSubmit} className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What are you looking for?"
          disabled={isLoading}
          className="w-full h-14 pl-12 pr-28 text-base bg-white border border-gray-200 rounded-2xl shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed placeholder:text-gray-400"
        />
        <svg
          className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
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
          className="absolute right-2 top-1/2 -translate-y-1/2 h-10 px-5 bg-orange-500 text-white font-semibold rounded-xl hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 active:scale-95"
        >
          {isLoading ? (
            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            "Search"
          )}
          .{" "}
        </button>
      </form>
      <div className="flex flex-wrap gap-2 justify-center">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => {
              setQuery(ex);
              onSearch(ex);
            }}
            disabled={isLoading}
            className="px-3 py-2 text-sm bg-white border border-gray-200 rounded-full text-gray-600 hover:border-orange-300 hover:text-orange-600 hover:bg-orange-50 transition-colors disabled:opacity-50 active:scale-95"
          >
            {ex}
          </button>
        ))}
      </div>
    </div>
  );
}
