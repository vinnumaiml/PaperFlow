"use client";

import React, { useState } from "react";
import Link from "next/link";
import { searchTools, CATEGORIES, ToolCategory } from "@/lib/tools/registry";
import { ToolIcon } from "@/components/ui/icons";
import { Search, X, ArrowRight } from "lucide-react";

export function ToolSearch() {
  const [query, setQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<ToolCategory | "All">("All");

  const results = searchTools(query).filter(
    (t) => selectedCategory === "All" || t.category === selectedCategory
  );

  return (
    <div className="w-full max-w-4xl mx-auto px-4 -mt-6 relative z-20">
      {/* Search Input Box */}
      <div className="bg-[#FFFFFF] dark:bg-[#14182B] rounded-2xl shadow-xl shadow-black/5 border border-[#E2E6F0] dark:border-[#2B3450] p-2 sm:p-3 transition-all focus-within:ring-2 focus-within:ring-[#A5B4FC]">
        <div className="relative flex items-center">
          <Search className="absolute left-4 w-5 h-5 text-[#788198] dark:text-[#939DB8]" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search all 40 PDF tools (e.g. compress, merge, word, redact, ocr, split)..."
            className="w-full pl-12 pr-10 py-3 text-sm sm:text-base bg-transparent text-[#171A33] dark:text-[#F4F6FF] placeholder:text-[#788198] dark:placeholder:text-[#939DB8] focus:outline-none"
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="absolute right-3 p-1.5 rounded-lg text-[#788198] hover:text-[#171A33] dark:text-[#939DB8] dark:hover:text-[#F4F6FF] transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pt-2 pb-1 scrollbar-none border-t border-[#E9ECF4] dark:border-[#252E47] px-1">
          <button
            onClick={() => setSelectedCategory("All")}
            className={`px-3 py-1 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
              selectedCategory === "All"
                ? "bg-[#5146D8] dark:bg-[#7568F2] text-white shadow-2xs"
                : "bg-[#F1F3F9] dark:bg-[#1A2036] text-[#555D75] dark:text-[#C0C7DC] hover:text-[#171A33] dark:hover:text-[#F4F6FF] hover:bg-[#E2E6F0] dark:hover:bg-[#2B3450]"
            }`}
          >
            All Tools
          </button>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                selectedCategory === cat
                  ? "bg-[#5146D8] dark:bg-[#7568F2] text-white shadow-2xs"
                  : "bg-[#F1F3F9] dark:bg-[#1A2036] text-[#555D75] dark:text-[#C0C7DC] hover:text-[#171A33] dark:hover:text-[#F4F6FF] hover:bg-[#E2E6F0] dark:hover:bg-[#2B3450]"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Real-time search dropdown/results when active query */}
      {query.trim().length > 0 && (
        <div className="mt-3 bg-[#FFFFFF] dark:bg-[#14182B] rounded-2xl shadow-2xl border border-[#E2E6F0] dark:border-[#2B3450] p-4 max-h-[420px] overflow-y-auto">
          <div className="text-xs font-semibold text-[#788198] dark:text-[#939DB8] uppercase tracking-wider mb-3 px-1">
            Matching Tools ({results.length})
          </div>
          {results.length === 0 ? (
            <div className="py-8 text-center text-sm text-[#788198] dark:text-[#939DB8]">
              No tools matching &quot;{query}&quot;. Try searching for &quot;compress&quot;, &quot;merge&quot;, or &quot;excel&quot;.
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {results.map((tool) => (
                <Link
                  key={tool.slug}
                  href={`/tools/${tool.slug}`}
                  className="flex items-start gap-3 p-3 rounded-xl hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] border border-transparent hover:border-[#E2E6F0] dark:hover:border-[#2B3450] transition-all group"
                >
                  <div className="w-10 h-10 rounded-xl bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#7568F2] flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                    <ToolIcon name={tool.icon} className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-semibold text-[#171A33] dark:text-[#F4F6FF] group-hover:text-[#5146D8] dark:group-hover:text-[#7568F2] transition-colors">
                        {tool.displayName}
                      </h4>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#F1F3F9] dark:bg-[#1A2036] text-[#788198] dark:text-[#939DB8] font-medium">
                        {tool.category}
                      </span>
                    </div>
                    <p className="text-xs text-[#555D75] dark:text-[#C0C7DC] line-clamp-1 mt-0.5">
                      {tool.description}
                    </p>
                  </div>
                  <ArrowRight className="w-4 h-4 text-[#788198] opacity-0 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all self-center" />
                </Link>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
