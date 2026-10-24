"use client";

import React from "react";
import { Shield, Zap, FileText } from "lucide-react";
import { motion } from "framer-motion";

export function Hero() {
  return (
    <section className="relative overflow-hidden pt-12 pb-16 md:pt-18 md:pb-20 border-b border-[#E2E6F0] dark:border-[#2B3450] bg-[#F7F8FC] dark:bg-[#0D1020] transition-colors">
      {/* Subtle Soft Background Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[720px] h-[320px] bg-gradient-to-tr from-[#5146D8]/8 via-[#8B5CF6]/6 to-[#0F9F91]/6 rounded-full blur-3xl pointer-events-none -z-10" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Brand Suite Badge */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#EEEDFF] dark:bg-[#29264E] border border-[#CECBFF] dark:border-[#3C4768] text-[#5146D8] dark:text-[#A5B4FC] text-xs font-semibold mb-6 shadow-2xs"
        >
          <span>Complete 40-Tool Suite • True Document Processing</span>
        </motion.div>

        {/* Hero Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-[#171A33] dark:text-[#F4F6FF] max-w-4xl mx-auto leading-tight sm:leading-tight"
        >
          Everything you need to{" "}
          <span
            style={{
              backgroundImage: "linear-gradient(135deg, #5146D8 0%, #7657E8 55%, #8B5CF6 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            work with PDFs.
          </span>
        </motion.h1>

        {/* Supporting Line */}
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-6 text-base sm:text-lg text-[#555D75] dark:text-[#C0C7DC] max-w-2xl mx-auto leading-relaxed"
        >
          Fast, private, and precise. Merge, split, edit, redact, and optimize with intelligent custom target-size compression—all running on isolated document engines.
        </motion.p>

        {/* Feature Highlights */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-[#788198] dark:text-[#939DB8] font-medium"
        >
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-[#0F9F91]" />
            <span>Target Size Search Compression</span>
          </div>
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-[#8B5CF6]" />
            <span>Deep Irreversible Redaction</span>
          </div>
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-[#5146D8] dark:text-[#7568F2]" />
            <span>Word, Excel & PPTX Conversions</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
