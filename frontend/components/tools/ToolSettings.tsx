"use client";

import React from "react";
import {
  Sliders,
  Sparkles,
  AlertCircle,
  Lock,
  Maximize,
  Tag,
  FileMinus,
  Sparkle,
  FileText,
  Table,
  Layers,
} from "lucide-react";

interface ToolSettingsProps {
  toolSlug: string;
  options: Record<string, any>;
  onChange: (newOptions: Record<string, any>) => void;
  pdfInfo?: { page_count?: number; metadata?: Record<string, string> } | null;
}

export function ToolSettings({ toolSlug, options, onChange }: ToolSettingsProps) {
  const update = (key: string, val: any) => {
    onChange({ ...options, [key]: val });
  };

  if (toolSlug === "compress-pdf") {
    const isCustom = options.preset === "custom";

    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-5">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <Sliders className="w-4 h-4" />
          Compression Mode & Target Size
        </div>

        {/* Preset Selector */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {[
            { id: "recommended", label: "Recommended", desc: "Best balance" },
            { id: "smaller_file", label: "Smaller File", desc: "Compact size" },
            { id: "high_quality", label: "High Quality", desc: "Mild compression" },
            { id: "custom", label: "Target Size", desc: "Exact Max KB" },
          ].map((preset) => (
            <button
              key={preset.id}
              type="button"
              onClick={() => update("preset", preset.id)}
              className={`p-3 rounded-xl border text-left transition-all ${
                options.preset === preset.id
                  ? "border-[#5146D8] dark:border-[#7568F2] bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#F4F6FF]"
                  : "border-[#E2E6F0] dark:border-[#2B3450] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] text-[#171A33] dark:text-[#F4F6FF]"
              }`}
            >
              <div className="text-xs font-bold">{preset.label}</div>
              <div className="text-[10px] text-[#788198] dark:text-[#939DB8] mt-0.5">{preset.desc}</div>
            </button>
          ))}
        </div>

        {/* Custom Target Size Controls */}
        {isCustom && (
          <div className="p-4 rounded-xl bg-[#EEEDFF]/60 dark:bg-[#29264E]/60 border border-[#CECBFF] dark:border-[#3C4768] space-y-3">
            <label className="block text-xs font-bold text-[#171A33] dark:text-[#F4F6FF]">
              Desired Maximum Output Size (KB)
            </label>
            <div className="flex items-center gap-3">
              <input
                type="number"
                min={10}
                max={50000}
                value={options.custom_target_kb || 500}
                onChange={(e) => update("custom_target_kb", parseInt(e.target.value) || 100)}
                className="w-36 px-3 py-2 rounded-lg bg-[#FFFFFF] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm font-semibold text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
              />
              <span className="text-xs text-[#788198] dark:text-[#939DB8] font-medium">KB (Kilobytes)</span>
            </div>
            <p className="text-[11px] text-[#555D75] dark:text-[#C0C7DC] leading-relaxed">
              The real compression search engine will test candidate downsampling rates and pick the highest-quality valid candidate that satisfies this maximum.
            </p>
          </div>
        )}

        {/* Aggressive downsampling toggle */}
        <label className="flex items-center gap-2.5 text-xs text-[#555D75] dark:text-[#C0C7DC] cursor-pointer pt-1">
          <input
            type="checkbox"
            checked={!!options.aggressive}
            onChange={(e) => update("aggressive", e.target.checked)}
            className="rounded border-[#CCD2E2] dark:border-[#3C4768] accent-[#5146D8] dark:accent-[#7568F2] focus:ring-[#A5B4FC] w-4 h-4"
          />
          <span>Enable aggressive raster image downsampling (allows lower minimum quality threshold)</span>
        </label>
      </div>
    );
  }

  if (toolSlug === "split-pdf") {
    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <Sliders className="w-4 h-4" />
          Split Configuration
        </div>

        <div className="grid grid-cols-3 gap-2">
          {[
            { id: "ranges", label: "By Ranges", desc: "e.g. 1-3, 5" },
            { id: "extract_all", label: "Every Page", desc: "Single page PDFs" },
            { id: "fixed_groups", label: "Fixed Groups", desc: "Every N pages" },
          ].map((mode) => (
            <button
              key={mode.id}
              type="button"
              onClick={() => update("mode", mode.id)}
              className={`p-3 rounded-xl border text-left transition-all ${
                options.mode === mode.id
                  ? "border-[#5146D8] dark:border-[#7568F2] bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#F4F6FF]"
                  : "border-[#E2E6F0] dark:border-[#2B3450] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] text-[#171A33] dark:text-[#F4F6FF]"
              }`}
            >
              <div className="text-xs font-bold">{mode.label}</div>
              <div className="text-[10px] text-[#788198] dark:text-[#939DB8] mt-0.5">{mode.desc}</div>
            </button>
          ))}
        </div>

        {options.mode === "ranges" && (
          <div>
            <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1.5">
              Page Range Expression
            </label>
            <input
              type="text"
              value={options.ranges || "1"}
              onChange={(e) => update("ranges", e.target.value)}
              placeholder="e.g. 1-3, 5, 7-10"
              className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
            />
          </div>
        )}

        {options.mode === "fixed_groups" && (
          <div>
            <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1.5">
              Pages per chunk
            </label>
            <input
              type="number"
              min={1}
              max={100}
              value={options.group_size || 2}
              onChange={(e) => update("group_size", parseInt(e.target.value) || 1)}
              className="w-32 px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
            />
          </div>
        )}
      </div>
    );
  }

  if (toolSlug === "resize-pdf") {
    const targetSize = options.target_size || "A4";
    const orientation = options.orientation || "portrait";
    const fitContent = options.fit_content !== false;
    const margin = options.margin ?? 0;

    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-5">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <Maximize className="w-4 h-4" />
          Page Geometry & Sizing Options
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1.5">
              Target Standard Dimensions
            </label>
            <select
              value={targetSize}
              onChange={(e) => update("target_size", e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] font-medium focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
            >
              <option value="A4">A4 (210 × 297 mm)</option>
              <option value="Letter">US Letter (8.5 × 11 in)</option>
              <option value="Legal">US Legal (8.5 × 14 in)</option>
              <option value="A3">A3 (297 × 420 mm)</option>
              <option value="Tabloid">Tabloid / Ledger (11 × 17 in)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1.5">
              Orientation
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => update("orientation", "portrait")}
                className={`py-2 px-3 rounded-lg border text-xs font-semibold text-center transition-all ${
                  orientation === "portrait"
                    ? "border-[#5146D8] dark:border-[#7568F2] bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#F4F6FF]"
                    : "border-[#E2E6F0] dark:border-[#2B3450] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] text-[#171A33] dark:text-[#F4F6FF]"
                }`}
              >
                Portrait
              </button>
              <button
                type="button"
                onClick={() => update("orientation", "landscape")}
                className={`py-2 px-3 rounded-lg border text-xs font-semibold text-center transition-all ${
                  orientation === "landscape"
                    ? "border-[#5146D8] dark:border-[#7568F2] bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#F4F6FF]"
                    : "border-[#E2E6F0] dark:border-[#2B3450] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] text-[#171A33] dark:text-[#F4F6FF]"
                }`}
              >
                Landscape
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
          <div>
            <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1.5">
              Margins (points)
            </label>
            <input
              type="number"
              min={0}
              max={100}
              value={margin}
              onChange={(e) => update("margin", parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
            />
          </div>

          <div className="flex items-center pt-5">
            <label className="flex items-center gap-2.5 text-xs text-[#555D75] dark:text-[#C0C7DC] cursor-pointer">
              <input
                type="checkbox"
                checked={fitContent}
                onChange={(e) => update("fit_content", e.target.checked)}
                className="rounded border-[#CCD2E2] dark:border-[#3C4768] accent-[#5146D8] dark:accent-[#7568F2] focus:ring-[#A5B4FC] w-4 h-4"
              />
              <span>Scale & center content to fit within new page boundaries</span>
            </label>
          </div>
        </div>
      </div>
    );
  }

  if (toolSlug === "pdf-metadata") {
    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <Tag className="w-4 h-4" />
          Document Metadata Properties
        </div>
        <p className="text-xs text-[#788198] dark:text-[#939DB8]">
          Modify internal PDF document properties, author information, and search indexing keywords.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1">
              Document Title
            </label>
            <input
              type="text"
              value={options.title || ""}
              onChange={(e) => update("title", e.target.value)}
              placeholder="e.g. Annual Financial Statement"
              className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1">
              Author / Organization
            </label>
            <input
              type="text"
              value={options.author || ""}
              onChange={(e) => update("author", e.target.value)}
              placeholder="e.g. Acme Corporation"
              className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1">
              Subject
            </label>
            <input
              type="text"
              value={options.subject || ""}
              onChange={(e) => update("subject", e.target.value)}
              placeholder="e.g. Q4 Performance Analysis"
              className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1">
              Keywords (comma-separated)
            </label>
            <input
              type="text"
              value={options.keywords || ""}
              onChange={(e) => update("keywords", e.target.value)}
              placeholder="finance, report, 2026, audit"
              className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1">
            Application / Creator
          </label>
          <input
            type="text"
            value={options.creator || ""}
            onChange={(e) => update("creator", e.target.value)}
            placeholder="e.g. PaperFlow Studio"
            className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
          />
        </div>
      </div>
    );
  }

  if (toolSlug === "remove-blank-pages") {
    const sensitivity = options.sensitivity ?? 0.992;
    const percentDisplay = (sensitivity * 100).toFixed(1);

    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <FileMinus className="w-4 h-4" />
          Blank Page Detection Heuristics
        </div>
        <p className="text-xs text-[#555D75] dark:text-[#C0C7DC] leading-relaxed">
          PaperFlow scans both structural text layers and raster pixel luminance distributions to safely detect empty divider pages without false-positive removals of signatures, diagrams, or stamps.
        </p>

        <div className="space-y-2 pt-2">
          <div className="flex justify-between items-center text-xs">
            <span className="font-semibold text-[#171A33] dark:text-[#F4F6FF]">White Background Sensitivity</span>
            <span className="font-bold text-[#5146D8] dark:text-[#7568F2]">{percentDisplay}%</span>
          </div>
          <input
            type="range"
            min={0.98}
            max={0.998}
            step={0.001}
            value={sensitivity}
            onChange={(e) => update("sensitivity", parseFloat(e.target.value))}
            className="w-full accent-[#5146D8] dark:accent-[#7568F2]"
          />
          <div className="flex justify-between text-[10px] text-[#788198] dark:text-[#939DB8]">
            <span>Aggressive (98.0%)</span>
            <span>Recommended (99.2%)</span>
            <span>Strict (99.8%)</span>
          </div>
        </div>
      </div>
    );
  }

  if (toolSlug === "deskew-pdf") {
    const deskew = options.deskew !== false;
    const enhanceContrast = options.enhance_contrast !== false;

    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <Sparkle className="w-4 h-4" />
          Scan Cleaning & Deskew Configuration
        </div>
        <p className="text-xs text-[#555D75] dark:text-[#C0C7DC] leading-relaxed">
          Evaluates horizontal projection profile variances between -4° and +4° to detect page skew, auto-rotate crooked pages, and enhance text contrast for OCR clarity.
        </p>

        <div className="space-y-3 pt-1">
          <label className="flex items-center gap-2.5 text-xs text-[#555D75] dark:text-[#C0C7DC] cursor-pointer">
            <input
              type="checkbox"
              checked={deskew}
              onChange={(e) => update("deskew", e.target.checked)}
              className="rounded border-[#CCD2E2] dark:border-[#3C4768] accent-[#5146D8] dark:accent-[#7568F2] focus:ring-[#A5B4FC] w-4 h-4"
            />
            <span className="font-medium">Automatic angle deskew (corrects slight rotational tilt)</span>
          </label>

          <label className="flex items-center gap-2.5 text-xs text-[#555D75] dark:text-[#C0C7DC] cursor-pointer">
            <input
              type="checkbox"
              checked={enhanceContrast}
              onChange={(e) => update("enhance_contrast", e.target.checked)}
              className="rounded border-[#CCD2E2] dark:border-[#3C4768] accent-[#5146D8] dark:accent-[#7568F2] focus:ring-[#A5B4FC] w-4 h-4"
            />
            <span className="font-medium">Autocontrast & sharpness enhancement (cleans background noise)</span>
          </label>
        </div>
      </div>
    );
  }

  if (toolSlug === "extract-text") {
    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <FileText className="w-4 h-4" />
          Text Extraction Settings
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1.5">
            Page Selection (leave as &quot;all&quot; for full document)
          </label>
          <input
            type="text"
            value={options.pages || "all"}
            onChange={(e) => update("pages", e.target.value)}
            placeholder="all, or 1-3, 5"
            className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
          />
          <p className="text-[11px] text-[#788198] dark:text-[#939DB8] mt-1.5">
            Extracts searchable UTF-8 text streams with paragraph spacing. Results can be downloaded as a text file or copied directly to clipboard.
          </p>
        </div>
      </div>
    );
  }

  if (toolSlug === "extract-tables") {
    const tableFormat = options.table_format || "csv";

    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <Table className="w-4 h-4" />
          Table Extraction Output Format
        </div>

        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => update("table_format", "csv")}
            className={`p-3 rounded-xl border text-center transition-all ${
              tableFormat === "csv"
                ? "border-[#5146D8] dark:border-[#7568F2] bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#F4F6FF]"
                : "border-[#E2E6F0] dark:border-[#2B3450] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] text-[#171A33] dark:text-[#F4F6FF]"
            }`}
          >
            <div className="text-xs font-bold">CSV Spreadsheet</div>
            <div className="text-[10px] text-[#788198] dark:text-[#939DB8] mt-0.5">Comma-separated values (.csv)</div>
          </button>
          <button
            type="button"
            onClick={() => update("table_format", "xlsx")}
            className={`p-3 rounded-xl border text-center transition-all ${
              tableFormat === "xlsx"
                ? "border-[#5146D8] dark:border-[#7568F2] bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#F4F6FF]"
                : "border-[#E2E6F0] dark:border-[#2B3450] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] text-[#171A33] dark:text-[#F4F6FF]"
            }`}
          >
            <div className="text-xs font-bold">Microsoft Excel</div>
            <div className="text-[10px] text-[#788198] dark:text-[#939DB8] mt-0.5">Styled multi-table sheet (.xlsx)</div>
          </button>
        </div>
      </div>
    );
  }

  if (toolSlug === "flatten-form") {
    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-3">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <Layers className="w-4 h-4" />
          Form Field Flattening
        </div>
        <p className="text-xs text-[#555D75] dark:text-[#C0C7DC] leading-relaxed">
          Permanent vector rasterization converts all interactive AcroForm form fields, checkboxes, radio selections, and signatures into permanent vector page content.
        </p>
        <div className="p-3 rounded-xl bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-[11px] text-[#555D75] dark:text-[#C0C7DC]">
          ✓ Prevents further editing or tampering of signed forms<br />
          ✓ Ensures consistent rendering across all mobile & desktop PDF viewers
        </div>
      </div>
    );
  }

  if (toolSlug === "protect-pdf") {
    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <Lock className="w-4 h-4" />
          AES-256 Encryption Password
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1">
              Set Password
            </label>
            <input
              type="password"
              value={options.password || ""}
              onChange={(e) => update("password", e.target.value)}
              placeholder="Enter strong encryption password"
              className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
            />
          </div>

          <div className="flex gap-4 pt-1">
            <label className="flex items-center gap-2 text-xs text-[#555D75] dark:text-[#C0C7DC] cursor-pointer">
              <input
                type="checkbox"
                checked={options.allow_printing !== false}
                onChange={(e) => update("allow_printing", e.target.checked)}
                className="rounded border-[#CCD2E2] dark:border-[#3C4768] accent-[#5146D8] dark:accent-[#7568F2] focus:ring-[#A5B4FC]"
              />
              Allow Printing
            </label>
            <label className="flex items-center gap-2 text-xs text-[#555D75] dark:text-[#C0C7DC] cursor-pointer">
              <input
                type="checkbox"
                checked={options.allow_copying !== false}
                onChange={(e) => update("allow_copying", e.target.checked)}
                className="rounded border-[#CCD2E2] dark:border-[#3C4768] accent-[#5146D8] dark:accent-[#7568F2] focus:ring-[#A5B4FC]"
              />
              Allow Content Copying
            </label>
          </div>
        </div>
      </div>
    );
  }

  if (toolSlug === "unlock-pdf") {
    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <Lock className="w-4 h-4" />
          Document Password
        </div>
        <div>
          <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1">
            Password to Unlock
          </label>
          <input
            type="password"
            value={options.password || ""}
            onChange={(e) => update("password", e.target.value)}
            placeholder="Enter password"
            className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
          />
        </div>
      </div>
    );
  }

  if (toolSlug === "add-watermark") {
    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <Sliders className="w-4 h-4" />
          Watermark Options
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1">
              Watermark Text
            </label>
            <input
              type="text"
              value={options.text || "CONFIDENTIAL"}
              onChange={(e) => update("text", e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1">
              Rotation Angle ({options.rotation || 45}°)
            </label>
            <input
              type="range"
              min={0}
              max={360}
              step={15}
              value={options.rotation || 45}
              onChange={(e) => update("rotation", parseInt(e.target.value))}
              className="w-full accent-[#5146D8] dark:accent-[#7568F2]"
            />
          </div>
        </div>
      </div>
    );
  }

  if (toolSlug === "rotate-pdf") {
    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <Sliders className="w-4 h-4" />
          Rotation Angle
        </div>
        <div className="grid grid-cols-3 gap-3">
          {[90, 180, 270].map((angle) => (
            <button
              key={angle}
              type="button"
              onClick={() => update("angle", angle)}
              className={`p-3 rounded-xl border text-center font-bold text-sm transition-all ${
                (options.angle || 90) === angle
                  ? "border-[#5146D8] dark:border-[#7568F2] bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#F4F6FF]"
                  : "border-[#E2E6F0] dark:border-[#2B3450] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] text-[#171A33] dark:text-[#F4F6FF]"
              }`}
            >
              Rotate {angle}°
            </button>
          ))}
        </div>
      </div>
    );
  }

  if (toolSlug === "redact-pdf") {
    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#B42318] dark:text-[#FDA29B]">
          <AlertCircle className="w-4 h-4" />
          Deep Text Redaction
        </div>
        <div>
          <label className="block text-xs font-semibold text-[#171A33] dark:text-[#F4F6FF] mb-1">
            Keywords or phrases to purge permanently (comma-separated)
          </label>
          <input
            type="text"
            value={(options.search_terms || []).join(", ")}
            onChange={(e) =>
              update(
                "search_terms",
                e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
              )
            }
            placeholder="e.g. Confidential, SSN, John Doe, Secret"
            className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#FDA29B]"
          />
          <p className="text-[11px] text-[#788198] dark:text-[#939DB8] mt-1.5">
            Content is permanently removed from the document stream, not just visually obscured.
          </p>
        </div>
      </div>
    );
  }

  if (toolSlug === "ai-summarize") {
    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <Sparkles className="w-4 h-4 text-[#8B5CF6]" />
          Summary Length
        </div>
        <div className="grid grid-cols-3 gap-2">
          {["short", "standard", "detailed"].map((len) => (
            <button
              key={len}
              type="button"
              onClick={() => update("length", len)}
              className={`p-3 rounded-xl border capitalize text-xs font-bold transition-all ${
                (options.length || "standard") === len
                  ? "border-[#5146D8] dark:border-[#7568F2] bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#F4F6FF]"
                  : "border-[#E2E6F0] dark:border-[#2B3450] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] text-[#171A33] dark:text-[#F4F6FF]"
              }`}
            >
              {len} Summary
            </button>
          ))}
        </div>
      </div>
    );
  }

  if (toolSlug === "ai-translate") {
    return (
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs space-y-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          <Sliders className="w-4 h-4 text-[#8B5CF6]" />
          Target Language
        </div>
        <select
          value={options.target_language || "Spanish"}
          onChange={(e) => update("target_language", e.target.value)}
          className="w-full px-3 py-2 rounded-lg bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-sm text-[#171A33] dark:text-[#F4F6FF] focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
        >
          {["Spanish", "French", "German", "Italian", "Portuguese", "Japanese", "Chinese", "Hindi", "Arabic"].map(
            (lang) => (
              <option key={lang} value={lang}>
                {lang}
              </option>
            )
          )}
        </select>
      </div>
    );
  }

  return null;
}
