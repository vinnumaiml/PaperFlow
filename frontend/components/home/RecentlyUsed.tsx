"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { getToolBySlug } from "@/lib/tools/registry";
import { ToolIcon } from "@/components/ui/icons";
import { History, X, ArrowRight } from "lucide-react";

export function RecentlyUsed() {
  const [recentSlugs, setRecentSlugs] = useState<string[]>([]);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("paperflow_recent_tools");
      if (stored) {
        setRecentSlugs(JSON.parse(stored).slice(0, 4));
      }
    } catch {
      // Ignore storage errors
    }
  }, []);

  const clearHistory = () => {
    try {
      localStorage.removeItem("paperflow_recent_tools");
      setRecentSlugs([]);
    } catch {
      // Ignore
    }
  };

  const validTools = recentSlugs.map((s) => getToolBySlug(s)).filter(Boolean);

  if (validTools.length === 0) return null;

  return (
    <section className="py-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-[#5146D8] dark:text-[#7568F2]" />
          <h3 className="text-sm font-bold text-[#171A33] dark:text-[#F4F6FF] uppercase tracking-wider">
            Recently Used
          </h3>
        </div>
        <button
          onClick={clearHistory}
          className="text-xs text-[#788198] dark:text-[#939DB8] hover:text-[#B42318] dark:hover:text-[#FDA29B] transition-colors flex items-center gap-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A5B4FC] rounded-lg px-2 py-1"
        >
          <X className="w-3.5 h-3.5" />
          Clear History
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {validTools.map((tool) => {
          if (!tool) return null;
          return (
            <Link
              key={tool.slug}
              href={`/tools/${tool.slug}`}
              className="flex items-center gap-3 p-3 rounded-xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] hover:border-[#CECBFF] dark:hover:border-[#5146D8] shadow-2xs hover:shadow-sm transition-all group"
            >
              <div className="w-9 h-9 rounded-lg bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#7568F2] flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                <ToolIcon name={tool.icon} className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-xs font-bold text-[#171A33] dark:text-[#F4F6FF] truncate group-hover:text-[#5146D8] dark:group-hover:text-[#7568F2]">
                  {tool.displayName}
                </div>
                <div className="text-[10px] text-[#788198] dark:text-[#939DB8] truncate">{tool.category}</div>
              </div>
              <ArrowRight className="w-3.5 h-3.5 text-[#788198] opacity-0 group-hover:opacity-100 transition-opacity" />
            </Link>
          );
        })}
      </div>
    </section>
  );
}
