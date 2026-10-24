"use client";

import React from "react";
import Link from "next/link";
import { CATEGORIES, CATEGORY_DESCRIPTIONS, getToolsByCategory } from "@/lib/tools/registry";
import {
  FolderTree,
  Zap,
  RefreshCw,
  Edit3,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  Layers,
} from "lucide-react";

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  "Organize PDF": FolderTree,
  "Compress, Repair and OCR": Zap,
  "Convert PDF": RefreshCw,
  "Edit PDF": Edit3,
  "Secure and Sign": ShieldCheck,
  "Extract and Understand": Sparkles,
};

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

export function BrowseByTask() {
  return (
    <section className="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2] mb-1">
            <Layers className="w-3.5 h-3.5" />
            Workflow Categories
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-[#171A33] dark:text-[#F4F6FF] tracking-tight">
            Browse by Task
          </h2>
        </div>
        <Link
          href="/tools"
          className="text-xs sm:text-sm font-semibold text-[#5146D8] dark:text-[#7568F2] hover:underline flex items-center gap-1"
        >
          View all 40 tools <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {CATEGORIES.map((category) => {
          const Icon = CATEGORY_ICONS[category] || Layers;
          const accent = CATEGORY_ACCENTS[category] || {
            iconColor: "text-[#5146D8] dark:text-[#7568F2]",
            bgColor: "bg-[#EEEDFF] dark:bg-[#29264E]",
          };
          const tools = getToolsByCategory(category);
          const catId = `category-${category.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;

          return (
            <Link
              key={category}
              href={`#${catId}`}
              className="flex flex-col p-6 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] hover:border-[#CECBFF] dark:hover:border-[#5146D8] shadow-2xs hover:shadow-lg hover:shadow-black/5 hover:-translate-y-0.5 transition-all group"
            >
              <div className="flex items-center justify-between mb-4">
                <div
                  className={`w-12 h-12 rounded-xl ${accent.bgColor} ${accent.iconColor} flex items-center justify-center group-hover:scale-105 transition-transform`}
                >
                  <Icon className="w-6 h-6" />
                </div>
                <span className="text-xs px-2.5 py-1 rounded-full bg-[#F1F3F9] dark:bg-[#1A2036] text-[#555D75] dark:text-[#C0C7DC] font-semibold">
                  {tools.length} Tools
                </span>
              </div>

              <h3 className="text-base font-bold text-[#171A33] dark:text-[#F4F6FF] group-hover:text-[#5146D8] dark:group-hover:text-[#7568F2] transition-colors">
                {category}
              </h3>

              <p className="text-xs text-[#555D75] dark:text-[#C0C7DC] mt-2 leading-relaxed flex-1">
                {CATEGORY_DESCRIPTIONS[category]}
              </p>

              <div className="mt-5 pt-3 border-t border-[#E9ECF4] dark:border-[#252E47] flex items-center justify-between text-xs font-semibold text-[#5146D8] dark:text-[#7568F2]">
                <span>Explore Tools</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
