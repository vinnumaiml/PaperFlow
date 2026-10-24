"use client";

import React from "react";
import Link from "next/link";
import { FileText, Lock } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-[#E2E6F0] dark:border-[#2B3450] bg-[#F7F8FC] dark:bg-[#0D1020] text-[#555D75] dark:text-[#C0C7DC] text-sm transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 lg:gap-12">
          {/* Brand Info */}
          <div className="md:col-span-1 space-y-4">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#5146D8] via-[#7657E8] to-[#8B5CF6] flex items-center justify-center text-white shadow-sm">
                <FileText className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-lg text-[#171A33] dark:text-[#F4F6FF]">
                PaperFlow
              </span>
            </div>
            <p className="text-xs leading-relaxed text-[#788198] dark:text-[#939DB8]">
              High-performance, secure online document processing suite. Convert, compress, protect, edit, and analyze PDFs with full privacy.
            </p>
            <div className="flex items-center gap-2 text-[11px] text-[#15803D] dark:text-[#6CE9A6] bg-[#ECFDF3] dark:bg-[#123528] px-3 py-1.5 rounded-lg border border-[#ABEFC6] dark:border-[#24684B]">
              <Lock className="w-3.5 h-3.5" />
              <span>Isolated Workspaces • Auto-Purged</span>
            </div>
          </div>

          {/* Categories 1 */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[#171A33] dark:text-[#F4F6FF] mb-3">
              Document Tools
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/tools/merge-pdf" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  Merge PDF
                </Link>
              </li>
              <li>
                <Link href="/tools/split-pdf" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  Split PDF
                </Link>
              </li>
              <li>
                <Link href="/tools/organize-pdf" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  Organize Pages
                </Link>
              </li>
              <li>
                <Link href="/tools/compress-pdf" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  Compress PDF (Target Size)
                </Link>
              </li>
              <li>
                <Link href="/tools/repair-pdf" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  Repair PDF
                </Link>
              </li>
              <li>
                <Link href="/tools/ocr-pdf" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  OCR Searchable PDF
                </Link>
              </li>
            </ul>
          </div>

          {/* Categories 2 */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[#171A33] dark:text-[#F4F6FF] mb-3">
              Conversions & Security
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/tools/pdf-to-word" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  PDF to Word (DOCX)
                </Link>
              </li>
              <li>
                <Link href="/tools/pdf-to-excel" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  PDF to Excel (XLSX)
                </Link>
              </li>
              <li>
                <Link href="/tools/protect-pdf" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  Protect PDF (AES-256)
                </Link>
              </li>
              <li>
                <Link href="/tools/unlock-pdf" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  Unlock PDF
                </Link>
              </li>
              <li>
                <Link href="/tools/redact-pdf" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  Deep Redaction
                </Link>
              </li>
              <li>
                <Link href="/tools/compare-pdf" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  Compare Two PDFs
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal & Trust */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[#171A33] dark:text-[#F4F6FF] mb-3">
              Trust & Security
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/privacy" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  Privacy Policy & Retention
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-[#555D75] dark:text-[#C0C7DC] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li className="text-[11px] leading-relaxed text-[#788198] dark:text-[#939DB8] pt-2">
                Uploaded documents are held in isolated temporary storage and automatically deleted after 60 minutes.
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-[#E9ECF4] dark:border-[#252E47] flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#788198] dark:text-[#939DB8]">
          <p>© 2026 PaperFlow. All processing engines operate on isolated servers.</p>
          <div className="flex items-center gap-6">
            <Link href="/privacy" className="hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
              Privacy
            </Link>
            <Link href="/terms" className="hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
              Terms
            </Link>
            <span className="text-[11px] text-[#0F9F91] dark:text-[#6CE9A6]">
              ● All Systems Operational
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
