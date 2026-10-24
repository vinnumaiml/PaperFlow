"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ToolDefinition } from "@/lib/tools/registry";
import { ToolIcon } from "@/components/ui/icons";
import { DropZone } from "@/components/upload/DropZone";
import { FileList } from "@/components/upload/FileList";
import { ToolSettings } from "@/components/tools/ToolSettings";
import { ResultCard } from "@/components/results/ResultCard";
import { PageOrganizer, PageItem } from "@/components/tools/PageOrganizer";
import { SignPad } from "@/components/tools/SignPad";
import { createJob, getJobStatus, JobResponse, inspectPdf } from "@/lib/api/client";
import {
  ChevronRight,
  Cpu,
  Loader2,
  ArrowRight,
} from "lucide-react";

interface ToolPageLayoutProps {
  tool: ToolDefinition;
}

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

export function ToolPageLayout({ tool }: ToolPageLayoutProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [options, setOptions] = useState<Record<string, any>>({
    preset: "recommended",
    custom_target_kb: 500,
    mode: "ranges",
    ranges: "1",
    angle: 90,
    text: "CONFIDENTIAL",
    target_language: "Spanish",
    length: "standard",
  });
  const [htmlContent, setHtmlContent] = useState("");
  const [pdfInfo, setPdfInfo] = useState<any>(null);
  const [organizerPages, setOrganizerPages] = useState<PageItem[]>([]);
  const [signatureData, setSignatureData] = useState<string>("");

  // Job processing state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentJob, setCurrentJob] = useState<JobResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const accent = CATEGORY_ACCENTS[tool.category] || {
    iconColor: "text-[#5146D8] dark:text-[#7568F2]",
    bgColor: "bg-[#EEEDFF] dark:bg-[#29264E]",
  };

  // When files change, inspect first PDF if applicable
  useEffect(() => {
    if (files.length > 0 && files[0].name.toLowerCase().endsWith(".pdf")) {
      inspectPdf(files[0])
        .then((info) => {
          setPdfInfo(info);
          if (tool.slug === "organize-pdf" && info.page_count) {
            const initialPages: PageItem[] = Array.from({ length: info.page_count }, (_, i) => ({
              page_num: i + 1,
              rotation: 0,
              duplicate_count: 1,
              deleted: false,
            }));
            setOrganizerPages(initialPages);
          }
          if (tool.slug === "pdf-metadata" && info.metadata) {
            setOptions((prev) => ({
              ...prev,
              title: info.metadata.title || "",
              author: info.metadata.author || "",
              subject: info.metadata.subject || "",
              keywords: info.metadata.keywords || "",
              creator: info.metadata.creator || "",
            }));
          }
        })
        .catch(() => {
          // Ignore inspect errors
        });
    } else {
      setPdfInfo(null);
      setOrganizerPages([]);
    }
  }, [files, tool.slug]);

  // Polling logic when job is queued/processing
  useEffect(() => {
    if (!currentJob || currentJob.status === "completed" || currentJob.status === "failed") {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const updated = await getJobStatus(currentJob.id);
        setCurrentJob(updated);
      } catch (err: any) {
        console.error("Polling error", err);
      }
    }, 800);

    return () => clearInterval(interval);
  }, [currentJob]);

  // Handle Submission
  const handleProcess = async () => {
    if (tool.slug !== "html-to-pdf" && files.length === 0) {
      setErrorMessage("Please select at least one file to process.");
      return;
    }
    if (tool.minFiles && files.length < tool.minFiles) {
      setErrorMessage(`This tool requires at least ${tool.minFiles} files.`);
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      if (typeof window !== "undefined") {
        try {
          const raw = localStorage.getItem("paperflow_recent_tools");
          const parsed = raw ? JSON.parse(raw) : [];
          const updated = [tool.slug, ...parsed.filter((s: string) => s !== tool.slug)].slice(0, 10);
          localStorage.setItem("paperflow_recent_tools", JSON.stringify(updated));
        } catch {
          // Ignore storage errors
        }
      }

      const finalOptions = { ...options };

      // Append organizer pages if tool is organize-pdf
      if (tool.slug === "organize-pdf" && organizerPages.length > 0) {
        finalOptions.pages = organizerPages;
      }

      // Append signature if tool is sign-pdf
      if (tool.slug === "sign-pdf" && signatureData) {
        finalOptions.signatures = [
          {
            page: 1,
            x: 100,
            y: 100,
            width: 160,
            height: 60,
            image_data: signatureData,
          },
        ];
      }

      const job = await createJob(
        tool.slug,
        files,
        finalOptions,
        tool.slug === "html-to-pdf" ? htmlContent : undefined
      );

      setCurrentJob(job);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to initiate processing.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setFiles([]);
    setCurrentJob(null);
    setErrorMessage(null);
    setPdfInfo(null);
  };

  return (
    <div className="min-h-screen py-10 bg-[#F7F8FC] dark:bg-[#0D1020] transition-colors">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Breadcrumbs */}
        <nav className="flex items-center gap-1.5 text-xs text-[#788198] dark:text-[#939DB8]">
          <Link href="/" className="hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors">
            Home
          </Link>
          <ChevronRight className="w-3.5 h-3.5 text-[#CCD2E2] dark:text-[#3C4768]" />
          <Link
            href={`/#category-${tool.category.toLowerCase().replace(/\s+/g, "-")}`}
            className="hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors"
          >
            {tool.category}
          </Link>
          <ChevronRight className="w-3.5 h-3.5 text-[#CCD2E2] dark:text-[#3C4768]" />
          <span className="font-semibold text-[#171A33] dark:text-[#F4F6FF]">
            {tool.displayName}
          </span>
        </nav>

        {/* Tool Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#E2E6F0] dark:border-[#2B3450]">
          <div className="flex items-center gap-4">
            <div
              className={`w-14 h-14 rounded-2xl ${accent.bgColor} ${accent.iconColor} flex items-center justify-center shrink-0 shadow-2xs border border-[#E2E6F0] dark:border-[#2B3450]`}
            >
              <ToolIcon name={tool.icon} className="w-7 h-7" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-[#171A33] dark:text-[#F4F6FF] tracking-tight">
                {tool.displayName}
              </h1>
              <p className="text-xs sm:text-sm text-[#555D75] dark:text-[#C0C7DC] mt-1 max-w-xl">
                {tool.longDescription}
              </p>
            </div>
          </div>

          <div className="flex sm:flex-col items-start sm:items-end gap-1 text-[11px] text-[#788198] dark:text-[#939DB8] shrink-0">
            <span className="flex items-center gap-1 font-semibold text-[#555D75] dark:text-[#C0C7DC]">
              <Cpu className="w-3.5 h-3.5 text-[#5146D8] dark:text-[#7568F2]" />
              {tool.requiredProcessingEngine.split("&")[0]}
            </span>
            <span className="text-[10px] text-[#15803D] dark:text-[#6CE9A6] bg-[#ECFDF3] dark:bg-[#123528] px-2.5 py-0.5 rounded-full border border-[#ABEFC6] dark:border-[#24684B] font-medium">
              Isolated Workspace
            </span>
          </div>
        </div>

        {/* If a job is running or completed */}
        {currentJob ? (
          <div className="space-y-6">
            {currentJob.status !== "completed" && currentJob.status !== "failed" && (
              <div className="p-8 rounded-3xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-xl space-y-6 text-center">
                <div className="w-16 h-16 rounded-full bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#7568F2] flex items-center justify-center mx-auto animate-pulse">
                  <Loader2 className="w-8 h-8 animate-spin" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-[#171A33] dark:text-[#F4F6FF]">
                    {currentJob.progress.step}...
                  </h3>
                  <p className="text-xs text-[#555D75] dark:text-[#C0C7DC] mt-1">
                    {currentJob.progress.message}
                  </p>
                </div>

                {/* Progress bar */}
                <div className="w-full max-w-md mx-auto bg-[#F1F3F9] dark:bg-[#1A2036] rounded-full h-2.5 overflow-hidden">
                  <div
                    style={{ width: `${currentJob.progress.percentage}%` }}
                    className="bg-[#5146D8] dark:bg-[#7568F2] h-full rounded-full transition-all duration-300"
                  />
                </div>
                <div className="text-xs font-semibold text-[#5146D8] dark:text-[#7568F2]">
                  {currentJob.progress.percentage}%
                </div>
              </div>
            )}

            {(currentJob.status === "completed" || currentJob.status === "failed") && (
              <ResultCard job={currentJob} onReset={handleReset} />
            )}
          </div>
        ) : (
          /* Normal Upload & Settings Flow */
          <div className="space-y-6">
            {/* HTML to PDF input */}
            {tool.slug === "html-to-pdf" ? (
              <div className="space-y-3 p-6 rounded-3xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs">
                <label className="block text-xs font-bold uppercase tracking-wider text-[#171A33] dark:text-[#F4F6FF]">
                  Enter HTML Markup or Web Content
                </label>
                <textarea
                  rows={8}
                  value={htmlContent}
                  onChange={(e) => setHtmlContent(e.target.value)}
                  placeholder="<h1>Invoice #1042</h1><p>Customer: John Doe</p>..."
                  className="w-full p-4 rounded-xl bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] font-mono text-xs text-[#171A33] dark:text-[#F4F6FF] leading-relaxed focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
                />
              </div>
            ) : (
              /* Drag & Drop Upload Zone */
              <div className="space-y-4">
                <DropZone
                  onFilesSelected={(newFiles) => {
                    if (tool.multipleFiles) {
                      setFiles((prev) => [...prev, ...newFiles]);
                    } else {
                      setFiles(newFiles.slice(0, 1));
                    }
                  }}
                  acceptedFormats={tool.acceptedInputFormats}
                  multiple={tool.multipleFiles}
                  maxSizeMB={tool.maxAcceptedFileSizeMB}
                  allowCamera={tool.slug === "scan-to-pdf"}
                />

                <FileList
                  files={files}
                  onRemove={(idx) => setFiles((prev) => prev.filter((_, i) => i !== idx))}
                  onReorder={(reordered) => setFiles(reordered)}
                  allowReorder={tool.multipleFiles}
                />
              </div>
            )}

            {/* Specialized tool settings */}
            <ToolSettings
              toolSlug={tool.slug}
              options={options}
              onChange={setOptions}
              pdfInfo={pdfInfo}
            />

            {/* Specialized Page Organizer for organize-pdf */}
            {tool.slug === "organize-pdf" && organizerPages.length > 0 && (
              <PageOrganizer pages={organizerPages} onChange={setOrganizerPages} />
            )}

            {/* Specialized Signature Pad for sign-pdf */}
            {tool.slug === "sign-pdf" && (
              <SignPad onSignatureReady={setSignatureData} />
            )}

            {/* Error Message */}
            {errorMessage && (
              <div className="p-4 rounded-2xl bg-[#FEF3F2] dark:bg-[#401C21] border border-[#FECDCA] dark:border-[#7A2E35] text-xs text-[#B42318] dark:text-[#FDA29B] font-medium">
                {errorMessage}
              </div>
            )}

            {/* Primary Action Button */}
            <div className="pt-2">
              <button
                type="button"
                onClick={handleProcess}
                disabled={isSubmitting || (tool.slug !== "html-to-pdf" && files.length === 0)}
                className="w-full py-3.5 sm:py-4 rounded-xl bg-[#5146D8] hover:bg-[#4338B8] active:bg-[#373099] dark:bg-[#7568F2] dark:hover:bg-[#887DFB] text-white font-bold text-sm sm:text-base shadow-sm hover:shadow-md transition-all duration-150 flex items-center justify-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A5B4FC] disabled:bg-[#ECEEF5] dark:disabled:bg-[#1B2138] disabled:text-[#9299AC] dark:disabled:text-[#5A6482] disabled:cursor-not-allowed disabled:shadow-none"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Preparing Document...</span>
                  </>
                ) : (
                  <>
                    <span>{tool.actionButtonText}</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
