"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { CATEGORIES } from "@/lib/tools/registry";
import {
  FileText,
  Moon,
  Sun,
  Menu,
  X,
  ChevronDown,
  ShieldCheck,
} from "lucide-react";

export function Header() {
  const pathname = usePathname();
  const [isDark, setIsDark] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [categoriesOpen, setCategoriesOpen] = useState(false);

  useEffect(() => {
    // Check initial theme from DOM or storage
    const hasDarkClass = document.documentElement.classList.contains("dark");
    const saved = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    if (saved === "dark" || (!saved && (hasDarkClass || prefersDark))) {
      setIsDark(true);
      document.documentElement.classList.add("dark");
    } else {
      setIsDark(false);
      document.documentElement.classList.remove("dark");
    }
  }, []);

  const toggleTheme = () => {
    if (isDark) {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
      setIsDark(false);
    } else {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
      setIsDark(true);
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-[#E2E6F0] dark:border-[#2B3450] bg-white/90 dark:bg-[#14182B]/90 backdrop-blur-md transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#5146D8] via-[#7657E8] to-[#8B5CF6] flex items-center justify-center text-white shadow-sm shadow-[#5146D8]/20 group-hover:scale-105 transition-transform">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-xl tracking-tight text-[#171A33] dark:text-[#F4F6FF]">
              PaperFlow
            </span>
            <span className="text-[10px] uppercase font-semibold tracking-wider text-[#5146D8] dark:text-[#7568F2]">
              PDF Studio
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1.5 lg:gap-2">
          <Link
            href="/tools"
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              pathname === "/tools"
                ? "bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#7568F2]"
                : "text-[#555D75] dark:text-[#C0C7DC] hover:text-[#171A33] dark:hover:text-[#F4F6FF] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036]"
            }`}
          >
            All Tools
          </Link>

          {/* Categories Dropdown */}
          <div className="relative">
            <button
              onClick={() => setCategoriesOpen(!categoriesOpen)}
              onBlur={() => setTimeout(() => setCategoriesOpen(false), 200)}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium text-[#555D75] dark:text-[#C0C7DC] hover:text-[#171A33] dark:hover:text-[#F4F6FF] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A5B4FC]"
            >
              Categories
              <ChevronDown className={`w-4 h-4 transition-transform ${categoriesOpen ? "rotate-180" : ""}`} />
            </button>

            {categoriesOpen && (
              <div className="absolute top-full left-0 mt-2 w-56 p-1.5 rounded-xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-xl shadow-black/10 z-50 flex flex-col gap-1 animate-in fade-in slide-in-from-top-2">
                {CATEGORIES.map((cat) => (
                  <Link
                    key={cat}
                    href={`/#category-${cat.toLowerCase().replace(/\s+/g, "-")}`}
                    className="px-3 py-2 rounded-lg text-xs font-medium text-[#555D75] dark:text-[#C0C7DC] hover:bg-[#EEEDFF] dark:hover:bg-[#29264E] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors"
                  >
                    {cat}
                  </Link>
                ))}
              </div>
            )}
          </div>

          <Link
            href="/privacy"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-[#555D75] dark:text-[#C0C7DC] hover:text-[#171A33] dark:hover:text-[#F4F6FF] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] transition-colors"
          >
            <ShieldCheck className="w-4 h-4 text-[#0F9F91]" />
            Security & Privacy
          </Link>
        </nav>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            aria-label="Toggle theme"
            className="p-2 rounded-xl text-[#555D75] hover:text-[#171A33] dark:text-[#C0C7DC] dark:hover:text-[#F4F6FF] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A5B4FC]"
          >
            {isDark ? <Sun className="w-5 h-5 text-[#FEC84B]" /> : <Moon className="w-5 h-5 text-[#5146D8]" />}
          </button>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
            className="md:hidden p-2 rounded-xl text-[#555D75] hover:text-[#171A33] dark:text-[#C0C7DC] dark:hover:text-[#F4F6FF] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A5B4FC]"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-[#E2E6F0] dark:border-[#2B3450] bg-[#FFFFFF] dark:bg-[#14182B] px-4 py-4 space-y-2">
          <Link
            href="/tools"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-[#171A33] dark:text-[#F4F6FF] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036]"
          >
            All PDF Tools
          </Link>
          <div className="pt-2 pb-1 border-t border-[#E9ECF4] dark:border-[#252E47] text-xs font-semibold uppercase text-[#788198] px-3">
            Tool Categories
          </div>
          {CATEGORIES.map((cat) => (
            <Link
              key={cat}
              href={`/#category-${cat.toLowerCase().replace(/\s+/g, "-")}`}
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-sm text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] hover:bg-[#EEEDFF] dark:hover:bg-[#29264E]"
            >
              {cat}
            </Link>
          ))}
          <div className="pt-2 border-t border-[#E9ECF4] dark:border-[#252E47]">
            <Link
              href="/privacy"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-[#555D75] dark:text-[#C0C7DC] hover:text-[#171A33] dark:hover:text-[#F4F6FF]"
            >
              <ShieldCheck className="w-4 h-4 text-[#0F9F91]" />
              Security & Privacy Policy
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
