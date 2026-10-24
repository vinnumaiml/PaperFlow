"use client";

import React from "react";
import Link from "next/link";
import { CATEGORIES, getToolsByCategory } from "@/lib/tools/registry";
import { ToolIcon } from "@/components/ui/icons";
import { ArrowRight, Layers } from "lucide-react";

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

export function CategorySections() {
  return (
    <section className="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
      {CATEGORIES.map((category) => {
        const tools = getToolsByCategory(category);
        const catId = `category-${category.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
        const accent = CATEGORY_ACCENTS[category] || {
          iconColor: "text-[#5146D8] dark:text-[#7568F2]",
          bgColor: "bg-[#EEEDFF] dark:bg-[#29264E]",
        };

        return (
          <div key={category} id={catId} className="scroll-mt-24">
            <div className="flex items-center gap-2.5 mb-6 pb-3 border-b border-[#E2E6F0] dark:border-[#2B3450]">
              <div
                className={`w-8 h-8 rounded-lg ${accent.bgColor} ${accent.iconColor} flex items-center justify-center font-bold text-xs`}
              >
                <Layers className="w-4 h-4" />
              </div>
              <h3 className="text-xl sm:text-2xl font-bold text-[#171A33] dark:text-[#F4F6FF] tracking-tight">
                {category}
              </h3>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#F1F3F9] dark:bg-[#1A2036] text-[#555D75] dark:text-[#C0C7DC] font-semibold">
                {tools.length} Tools
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {tools.map((tool) => (
                <Link
                  key={tool.slug}
                  href={`/tools/${tool.slug}`}
                  className="group relative flex flex-col p-4 rounded-xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] hover:border-[#CECBFF] dark:hover:border-[#5146D8] shadow-2xs hover:shadow-lg hover:shadow-black/5 hover:-translate-y-0.5 transition-all"
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`w-10 h-10 rounded-xl ${accent.bgColor} ${accent.iconColor} flex items-center justify-center shrink-0 transition-transform group-hover:scale-105`}
                    >
                      <ToolIcon name={tool.icon} className="w-5 h-5" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-bold text-[#171A33] dark:text-[#F4F6FF] group-hover:text-[#5146D8] dark:group-hover:text-[#7568F2] transition-colors flex items-center justify-between">
                        <span>{tool.displayName}</span>
                        <ArrowRight className="w-3.5 h-3.5 opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all text-[#5146D8] dark:text-[#7568F2]" />
                      </h4>
                      <p className="text-xs text-[#555D75] dark:text-[#C0C7DC] mt-1 line-clamp-2 leading-relaxed">
                        {tool.description}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 pt-2.5 border-t border-[#E9ECF4] dark:border-[#252E47] flex items-center justify-between text-[11px] text-[#788198] dark:text-[#939DB8]">
                    <span>Engine: {tool.requiredProcessingEngine.split("&")[0]}</span>
                    <span className="uppercase font-semibold text-[10px] text-[#555D75] dark:text-[#C0C7DC]">
                      {tool.supportedOutputFormats.join(" • ")}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        );
      })}
    </section>
  );
}
