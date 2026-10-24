"use client";

import React, { useEffect, useState } from "react";
import confetti from "canvas-confetti";
import { JobResponse, getDownloadUrl } from "@/lib/api/client";
import { formatBytes } from "@/lib/utils/cn";
import {
  CheckCircle2,
  AlertCircle,
  Download,
  RotateCcw,
  FileCheck,
  ArrowDownRight,
  Clock,
  Copy,
  Check,
  Sparkles,
  Layers,
  Table,
  FileMinus,
} from "lucide-react";

interface ResultCardProps {
  job: JobResponse;
  onReset: () => void;
}

export function ResultCard({ job, onReset }: ResultCardProps) {
  const isCompleted = job.status === "completed";
  const isFailed = job.status === "failed";
  const stats = job.stats || {};
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isCompleted) {
      try {
        confetti({
          particleCount: 50,
          spread: 60,
          origin: { y: 0.7 },
        });
      } catch {
        // Safe ignore
      }
    }
  }, [isCompleted]);

  const handleCopyText = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (isFailed) {
    return (
      <div className="w-full max-w-2xl mx-auto p-6 sm:p-8 rounded-3xl bg-[#FEF3F2] dark:bg-[#401C21] border border-[#FECDCA] dark:border-[#7A2E35] shadow-xl space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-white/80 dark:bg-black/20 text-[#B42318] dark:text-[#FDA29B] flex items-center justify-center shrink-0 border border-[#FECDCA] dark:border-[#7A2E35]">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-[#B42318] dark:text-[#FDA29B]">
              Processing Error
            </h3>
            <p className="text-xs text-[#B42318]/90 dark:text-[#FDA29B]/90 mt-0.5 font-medium">
              The operation could not be completed safely.
            </p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white/70 dark:bg-black/20 border border-[#FECDCA] dark:border-[#7A2E35] text-xs text-[#B42318] dark:text-[#FDA29B] leading-relaxed font-mono">
          {job.error || "An unexpected error occurred during processing."}
        </div>

        <button
          onClick={onReset}
          className="flex items-center justify-center gap-2 w-full py-3 rounded-xl bg-[#5146D8] dark:bg-[#7568F2] hover:bg-[#4338B8] dark:hover:bg-[#887DFB] text-white text-xs font-semibold shadow-md transition-all cursor-pointer"
        >
          <RotateCcw className="w-4 h-4" />
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="w-full max-w-2xl mx-auto p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-xl space-y-6 animate-in fade-in zoom-in-95 duration-300">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-[#E9ECF4] dark:border-[#252E47]">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-[#ECFDF3] dark:bg-[#123528] text-[#15803D] dark:text-[#6CE9A6] border border-[#ABEFC6] dark:border-[#24684B] flex items-center justify-center shrink-0">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-[#171A33] dark:text-[#F4F6FF]">
              Task Completed!
            </h3>
            <p className="text-xs text-[#555D75] dark:text-[#C0C7DC]">
              Your document has been processed and is ready for download.
            </p>
          </div>
        </div>

        {job.execution_time_seconds && (
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#F1F3F9] dark:bg-[#1A2036] text-[#555D75] dark:text-[#C0C7DC] border border-[#E2E6F0] dark:border-[#2B3450] text-xs font-medium">
            <Clock className="w-3.5 h-3.5" />
            <span>{job.execution_time_seconds}s</span>
          </div>
        )}
      </div>

      {/* Special Compression Stats Breakdown */}
      {job.tool === "compress-pdf" && stats.original_size && (
        <div className="p-4 rounded-2xl bg-[#EEEDFF]/60 dark:bg-[#29264E]/40 border border-[#CECBFF] dark:border-[#3C4768] space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#171A33] dark:text-[#F4F6FF]">
              Compression Search Outcome
            </span>
            {stats.target_achieved ? (
              <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#ECFDF3] dark:bg-[#123528] text-[#15803D] dark:text-[#6CE9A6] border border-[#ABEFC6] dark:border-[#24684B]">
                Target Achieved ✓
              </span>
            ) : (
              <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#FFFAEB] dark:bg-[#382A12] text-[#B54708] dark:text-[#FEC84B] border border-[#FEDF89] dark:border-[#6B4D1A]">
                Best Safe Quality Reached
              </span>
            )}
          </div>

          <div className="grid grid-cols-3 gap-2 text-center pt-1">
            <div className="p-2.5 rounded-xl bg-white dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450]">
              <div className="text-[10px] text-[#788198] dark:text-[#939DB8] uppercase font-semibold">Original</div>
              <div className="text-xs font-bold text-[#171A33] dark:text-[#F4F6FF] mt-0.5">
                {formatBytes(stats.original_size)}
              </div>
            </div>
            <div className="p-2.5 rounded-xl bg-white dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450]">
              <div className="text-[10px] text-[#788198] dark:text-[#939DB8] uppercase font-semibold">Compressed</div>
              <div className="text-xs font-bold text-[#5146D8] dark:text-[#7568F2] mt-0.5">
                {formatBytes(stats.output_size)}
              </div>
            </div>
            <div className="p-2.5 rounded-xl bg-white dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450]">
              <div className="text-[10px] text-[#788198] dark:text-[#939DB8] uppercase font-semibold">Saved</div>
              <div className="text-xs font-bold text-[#15803D] dark:text-[#6CE9A6] mt-0.5 flex items-center justify-center gap-0.5">
                <ArrowDownRight className="w-3.5 h-3.5" />
                {stats.reduction_percentage}%
              </div>
            </div>
          </div>

          <p className="text-[11px] text-[#555D75] dark:text-[#C0C7DC] pt-1">
            {stats.message}
          </p>
        </div>
      )}

      {/* Special Remove Blank Pages Breakdown */}
      {job.tool === "remove-blank-pages" && stats.removed_count !== undefined && (
        <div className="p-4 rounded-2xl bg-[#EEEDFF]/60 dark:bg-[#29264E]/40 border border-[#CECBFF] dark:border-[#3C4768] space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-[#171A33] dark:text-[#F4F6FF]">
            <FileMinus className="w-4 h-4 text-[#5146D8] dark:text-[#7568F2]" />
            <span>Blank Page Removal Report</span>
          </div>
          <div className="text-xs text-[#555D75] dark:text-[#C0C7DC] leading-relaxed">
            {stats.removed_count > 0 ? (
              <span>
                Detected and removed <strong className="text-[#171A33] dark:text-[#F4F6FF]">{stats.removed_count}</strong> blank page(s) (Page{" "}
                {stats.removed_pages.join(", ")}). Clean document contains{" "}
                <strong className="text-[#171A33] dark:text-[#F4F6FF]">{stats.resulting_page_count}</strong> page(s).
              </span>
            ) : (
              <span>No blank pages met the sensitivity threshold. All pages preserved.</span>
            )}
          </div>
        </div>
      )}

      {/* Special Extract Text Preview Box */}
      {job.tool === "extract-text" && (stats.preview_text || stats.preview_snippet) && (
        <div className="p-4 rounded-2xl bg-[#F1F3F9] dark:bg-[#1A2036] border border-[#E2E6F0] dark:border-[#2B3450] space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#171A33] dark:text-[#F4F6FF]">
              Extracted Text Preview ({stats.total_characters || 0} characters)
            </span>
            <button
              onClick={() => handleCopyText(stats.preview_text || stats.preview_snippet)}
              className="flex items-center gap-1 text-[11px] font-semibold text-[#5146D8] dark:text-[#7568F2] hover:underline cursor-pointer"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-[#15803D] dark:text-[#6CE9A6]" />
                  <span className="text-[#15803D] dark:text-[#6CE9A6]">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy Text</span>
                </>
              )}
            </button>
          </div>
          <div className="max-h-48 overflow-y-auto p-3 rounded-xl bg-white dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] text-xs font-mono text-[#171A33] dark:text-[#C0C7DC] whitespace-pre-wrap leading-relaxed select-all">
            {stats.preview_text || stats.preview_snippet}
          </div>
        </div>
      )}

      {/* Special Flatten Form Notice */}
      {job.tool === "flatten-form" && (
        <div className="p-4 rounded-2xl bg-[#ECFDF3]/60 dark:bg-[#123528]/50 border border-[#ABEFC6] dark:border-[#24684B] space-y-1">
          <div className="flex items-center gap-2 text-xs font-bold text-[#15803D] dark:text-[#6CE9A6]">
            <Layers className="w-4 h-4 text-[#15803D] dark:text-[#6CE9A6]" />
            <span>Form Fields Permanently Baked</span>
          </div>
          <p className="text-xs text-[#555D75] dark:text-[#C0C7DC]">
            All fillable inputs, checkmarks, and signatures across {stats.page_count || 1} pages have been flattened into static vector graphics.
          </p>
        </div>
      )}

      {/* Special Deskew & Clean Report */}
      {job.tool === "deskew-pdf" && (
        <div className="p-4 rounded-2xl bg-[#EEEDFF]/60 dark:bg-[#29264E]/40 border border-[#CECBFF] dark:border-[#3C4768] space-y-1">
          <div className="flex items-center gap-2 text-xs font-bold text-[#171A33] dark:text-[#F4F6FF]">
            <Sparkles className="w-4 h-4 text-[#5146D8] dark:text-[#7568F2]" />
            <span>Document Deskewed & Enhanced</span>
          </div>
          <p className="text-xs text-[#555D75] dark:text-[#C0C7DC]">
            Processed {stats.pages_processed || 1} page(s) with projection variance deskewing and contrast normalization.
          </p>
        </div>
      )}

      {/* Special Table Extraction Notice */}
      {job.tool === "extract-tables" && (
        <div className="p-4 rounded-2xl bg-[#EEEDFF]/60 dark:bg-[#29264E]/40 border border-[#CECBFF] dark:border-[#3C4768] space-y-1">
          <div className="flex items-center gap-2 text-xs font-bold text-[#171A33] dark:text-[#F4F6FF]">
            <Table className="w-4 h-4 text-[#5146D8] dark:text-[#7568F2]" />
            <span>Structured Data Extracted</span>
          </div>
          <p className="text-xs text-[#555D75] dark:text-[#C0C7DC]">
            Discovered {stats.tables_found || 0} table(s) and structured into {stats.format ? stats.format.toUpperCase() : "Spreadsheet"} format.
          </p>
        </div>
      )}

      {/* Special AI Summary Box */}
      {job.tool === "ai-summarize" && stats.summary && (
        <div className="p-4 rounded-2xl bg-[#EEEDFF]/60 dark:bg-[#29264E]/40 border border-[#CECBFF] dark:border-[#3C4768] space-y-3">
          <div className="text-xs font-bold text-[#171A33] dark:text-[#F4F6FF]">
            Executive Summary ({stats.engine || "PaperFlow"})
          </div>
          <p className="text-xs leading-relaxed text-[#555D75] dark:text-[#C0C7DC] whitespace-pre-wrap">
            {stats.summary}
          </p>
        </div>
      )}

      {/* Output Files Download Section */}
      <div className="space-y-3">
        <div className="text-xs font-bold text-[#788198] dark:text-[#939DB8] uppercase tracking-wider">
          Download Files ({job.outputs.length})
        </div>

        <div className="space-y-2">
          {job.outputs.map((out, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between gap-3 p-3.5 rounded-xl bg-[#F1F3F9] dark:bg-[#1A2036] border border-[#E2E6F0] dark:border-[#2B3450]"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-9 h-9 rounded-lg bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#7568F2] flex items-center justify-center shrink-0">
                  <FileCheck className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <div className="text-xs font-bold text-[#171A33] dark:text-[#F4F6FF] truncate">
                    {out.filename}
                  </div>
                  <div className="text-[11px] text-[#788198] dark:text-[#939DB8]">{formatBytes(out.size_bytes)}</div>
                </div>
              </div>

              <a
                href={getDownloadUrl(job.id, out.filename)}
                download={out.filename}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#5146D8] dark:bg-[#7568F2] hover:bg-[#4338B8] dark:hover:bg-[#887DFB] text-white text-xs font-semibold shadow-sm transition-all hover:scale-105 shrink-0 focus-ring"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download</span>
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* Reset Action */}
      <div className="pt-2 flex justify-center">
        <button
          onClick={onReset}
          className="flex items-center gap-2 text-xs font-semibold text-[#555D75] dark:text-[#C0C7DC] hover:text-[#171A33] dark:hover:text-[#F4F6FF] transition-colors cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Process another document
        </button>
      </div>
    </div>
  );
}
