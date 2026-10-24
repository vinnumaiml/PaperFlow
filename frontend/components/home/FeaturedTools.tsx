"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { TOOLS } from "@/lib/tools/registry";
import { ToolIcon } from "@/components/ui/icons";
import { ArrowRight, Sparkles } from "lucide-react";

const POPULAR_SLUGS = [
  "merge-pdf",
  "compress-pdf",
  "split-pdf",
  "pdf-to-word",
  "word-to-pdf",
  "jpg-to-pdf",
  "organize-pdf",
  "sign-pdf",
];

export function FeaturedTools() {
  const popularTools = POPULAR_SLUGS.map((slug) => TOOLS.find((t) => t.slug === slug)).filter(
    (t): t is NonNullable<typeof t> => t !== undefined
  );

  return (
    <section className="py-14 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2] mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            Most Popular
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-[#171A33] dark:text-[#F4F6FF] tracking-tight">
            Popular Tools
          </h2>
        </div>
        <p className="text-xs sm:text-sm text-[#788198] dark:text-[#939DB8] max-w-md">
          Immediate access to high-frequency PDF operations with zero configuration required.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {popularTools.map((tool, idx) => (
          <motion.div
            key={tool.slug}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: idx * 0.04 }}
          >
            <Link
              href={`/tools/${tool.slug}`}
              className="flex flex-col h-full p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs hover:shadow-lg hover:shadow-black/5 hover:border-[#CECBFF] dark:hover:border-[#5146D8] hover:-translate-y-0.5 transition-all group"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-11 h-11 rounded-xl bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#7568F2] flex items-center justify-center group-hover:scale-105 transition-transform">
                  <ToolIcon name={tool.icon} className="w-5 h-5" />
                </div>
                <span className="text-[10px] uppercase font-bold text-[#788198] dark:text-[#939DB8] px-2 py-0.5 rounded-md bg-[#F1F3F9] dark:bg-[#1A2036]">
                  {tool.supportedOutputFormats[0]}
                </span>
              </div>

              <h3 className="text-sm font-bold text-[#171A33] dark:text-[#F4F6FF] group-hover:text-[#5146D8] dark:group-hover:text-[#7568F2] transition-colors">
                {tool.displayName}
              </h3>

              <p className="text-xs text-[#555D75] dark:text-[#C0C7DC] mt-1.5 line-clamp-2 leading-relaxed flex-1">
                {tool.description}
              </p>

              <div className="mt-4 pt-3 border-t border-[#E9ECF4] dark:border-[#252E47] flex items-center justify-between text-xs font-semibold text-[#5146D8] dark:text-[#7568F2]">
                <span>Start Now</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
