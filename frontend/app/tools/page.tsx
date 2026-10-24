"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
import { TOOLS, CATEGORIES, ToolCategory } from "@/lib/tools/registry";
import { ToolIcon } from "@/components/ui/icons";
import { Search, X, ArrowRight, Sparkles, Layers } from "lucide-react";

const CATEGORY_ACCENTS: Record<
  string,
  {
    iconColor: string;
    bgColor: string;
  }
> = {
  "Organize PDF": {
    iconColor: "text-[#5146D8] dark:text-[#7568F2]",
    bgColor: "bg-[#EEEDFF] dark:bg-[#29264E]",
  },
  "Compress, Repair and OCR": {
    iconColor: "text-[#0F9F91] dark:text-[#0F9F91]",
    bgColor: "bg-[#E5FAF5] dark:bg-[#123528]",
  },
  "Convert PDF": {
    iconColor: "text-[#175CD3] dark:text-[#84CAFF]",
    bgColor: "bg-[#EFF8FF] dark:bg-[#152C46]",
  },
  "Edit PDF": {
    iconColor: "text-[#8B5CF6] dark:text-[#8B5CF6]",
    bgColor: "bg-[#F2EBFF] dark:bg-[#281F54]",
  },
  "Secure and Sign": {
    iconColor: "text-[#373099] dark:text-[#A5B4FC]",
    bgColor: "bg-[#EEEDFF] dark:bg-[#29264E]",
  },
  "Extract and Understand": {
    iconColor: "text-[#8B5CF6] dark:text-[#8B5CF6]",
    bgColor: "bg-[#F2EBFF] dark:bg-[#281F54]",
  },
};

export default function AllToolsPage() {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<ToolCategory | "All">("All");

  const filteredTools = useMemo(() => {
    const q = search.toLowerCase().trim();
    return TOOLS.filter((tool) => {
      const matchesCategory = selectedCategory === "All" || tool.category === selectedCategory;
      const matchesSearch =
        !q ||
        tool.displayName.toLowerCase().includes(q) ||
        tool.description.toLowerCase().includes(q) ||
        tool.category.toLowerCase().includes(q);
      return matchesCategory && matchesSearch;
    });
  }, [search, selectedCategory]);

  return (
    <div className="min-h-screen py-10 bg-[#F7F8FC] dark:bg-[#0D1020] transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-[#E2E6F0] dark:border-[#2B3450]">
          <div>
            <div className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2] mb-1">
              <Layers className="w-3.5 h-3.5" />
              Catalogue
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-[#171A33] dark:text-[#F4F6FF] tracking-tight">
              All PDF & Document Tools
            </h1>
            <p className="mt-2 text-sm text-[#555D75] dark:text-[#C0C7DC] max-w-xl">
              Explore our complete suite of 40 real document operations. Fast, private, and isolated.
            </p>
          </div>

          <div className="text-xs text-[#788198] dark:text-[#939DB8] font-medium">
            Showing <span className="font-bold text-[#171A33] dark:text-[#F4F6FF]">{filteredTools.length}</span> of {TOOLS.length} tools
          </div>
        </div>

        {/* Search & Filter Controls */}
        <div className="space-y-4">
          <div className="relative max-w-2xl">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[#788198] dark:text-[#939DB8]" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search tools by name, action, or format (e.g. compress, merge, word, metadata, blank)..."
              className="w-full pl-11 pr-10 py-3 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] text-sm text-[#171A33] dark:text-[#F4F6FF] placeholder:text-[#788198] dark:placeholder:text-[#939DB8] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC] shadow-2xs"
            />
            {search && (
              <button
                onClick={() => setSearch("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-[#788198] hover:text-[#171A33] dark:hover:text-[#F4F6FF]"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Category Filter Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
            <button
              onClick={() => setSelectedCategory("All")}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                selectedCategory === "All"
                  ? "bg-[#5146D8] dark:bg-[#7568F2] text-white shadow-2xs"
                  : "bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] text-[#555D75] dark:text-[#C0C7DC] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036]"
              }`}
            >
              All Categories
            </button>
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  selectedCategory === cat
                    ? "bg-[#5146D8] dark:bg-[#7568F2] text-white shadow-2xs"
                    : "bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] text-[#555D75] dark:text-[#C0C7DC] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036]"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Tools Grid */}
        {filteredTools.length === 0 ? (
          <div className="py-20 text-center rounded-3xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] p-8 space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-[#F1F3F9] dark:bg-[#1A2036] text-[#788198] flex items-center justify-center mx-auto">
              <Search className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-[#171A33] dark:text-[#F4F6FF]">
              No tools found
            </h3>
            <p className="text-xs text-[#788198] dark:text-[#939DB8] max-w-sm mx-auto">
              No document tool matches &quot;{search}&quot;. Try checking for spelling or resetting your category filter.
            </p>
            <button
              onClick={() => {
                setSearch("");
                setSelectedCategory("All");
              }}
              className="mt-2 px-4 py-2 rounded-xl bg-[#EEEDFF] dark:bg-[#29264E] text-xs font-semibold text-[#5146D8] dark:text-[#7568F2] hover:bg-[#CECBFF] dark:hover:bg-[#3C4768] transition-colors"
            >
              Reset Filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredTools.map((tool) => {
              const accent = CATEGORY_ACCENTS[tool.category] || {
                iconColor: "text-[#5146D8] dark:text-[#7568F2]",
                bgColor: "bg-[#EEEDFF] dark:bg-[#29264E]",
              };

              return (
                <Link
                  key={tool.slug}
                  href={`/tools/${tool.slug}`}
                  className="group relative flex flex-col p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] hover:border-[#CECBFF] dark:hover:border-[#5146D8] shadow-2xs hover:shadow-lg hover:shadow-black/5 hover:-translate-y-0.5 transition-all"
                >
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div
                      className={`w-11 h-11 rounded-xl ${accent.bgColor} ${accent.iconColor} flex items-center justify-center shrink-0 transition-transform group-hover:scale-105`}
                    >
                      <ToolIcon name={tool.icon} className="w-5 h-5" />
                    </div>

                    {tool.featured && (
                      <span className="flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#FFFAEB] dark:bg-[#382A12] text-[#B54708] dark:text-[#FEC84B] border border-[#FEDF89] dark:border-[#6B4D1A]">
                        <Sparkles className="w-3 h-3" />
                        Popular
                      </span>
                    )}
                  </div>

                  <h3 className="text-sm font-bold text-[#171A33] dark:text-[#F4F6FF] group-hover:text-[#5146D8] dark:group-hover:text-[#7568F2] transition-colors flex items-center justify-between">
                    <span>{tool.displayName}</span>
                    <ArrowRight className="w-3.5 h-3.5 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all text-[#5146D8] dark:text-[#7568F2]" />
                  </h3>

                  <p className="text-xs text-[#555D75] dark:text-[#C0C7DC] mt-1.5 line-clamp-2 leading-relaxed flex-1">
                    {tool.description}
                  </p>

                  <div className="mt-4 pt-3 border-t border-[#E9ECF4] dark:border-[#252E47] flex items-center justify-between text-[11px] text-[#788198] dark:text-[#939DB8]">
                    <span className="truncate max-w-[150px]">{tool.category}</span>
                    <span className="uppercase font-semibold text-[10px] text-[#555D75] dark:text-[#C0C7DC]">
                      {tool.supportedOutputFormats.join(" • ")}
                    </span>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
