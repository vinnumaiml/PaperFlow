"use client";

import React from "react";
import { RotateCw, Copy, Trash2, ArrowLeft, ArrowRight } from "lucide-react";

export interface PageItem {
  page_num: number;
  rotation: number;
  duplicate_count: number;
  deleted: boolean;
}

interface PageOrganizerProps {
  pages: PageItem[];
  onChange: (pages: PageItem[]) => void;
}

export function PageOrganizer({ pages, onChange }: PageOrganizerProps) {
  const rotatePage = (index: number) => {
    const next = [...pages];
    next[index].rotation = (next[index].rotation + 90) % 360;
    onChange(next);
  };

  const duplicatePage = (index: number) => {
    const next = [...pages];
    next[index].duplicate_count += 1;
    onChange(next);
  };

  const toggleDelete = (index: number) => {
    const next = [...pages];
    next[index].deleted = !next[index].deleted;
    onChange(next);
  };

  const movePage = (fromIndex: number, toIndex: number) => {
    if (toIndex < 0 || toIndex >= pages.length) return;
    const next = [...pages];
    const item = next[fromIndex];
    next.splice(fromIndex, 1);
    next.splice(toIndex, 0, item);
    onChange(next);
  };

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between text-xs font-semibold text-[#788198] dark:text-[#939DB8] uppercase px-1">
        <span>Document Pages ({pages.filter((p) => !p.deleted).length} active)</span>
        <span className="text-[11px] text-[#5146D8] dark:text-[#7568F2] font-medium">
          Click rotate, duplicate, or delete
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        {pages.map((item, idx) => (
          <div
            key={idx}
            className={`flex flex-col rounded-2xl border transition-all ${
              item.deleted
                ? "opacity-50 bg-[#ECEEF5] dark:bg-[#0D1020] border-[#E2E6F0] dark:border-[#2B3450]"
                : "bg-white dark:bg-[#14182B] border-[#E2E6F0] dark:border-[#2B3450] shadow-xs hover:border-[#CECBFF] dark:hover:border-[#5146D8]"
            }`}
          >
            {/* Visual page preview placeholder */}
            <div className="h-32 flex flex-col items-center justify-center p-3 border-b border-[#E9ECF4] dark:border-[#252E47] bg-[#F7F8FC] dark:bg-[#1A2036] rounded-t-2xl relative overflow-hidden">
              <div
                style={{ transform: `rotate(${item.rotation}deg)` }}
                className="w-16 h-22 bg-white dark:bg-[#14182B] border border-[#CCD2E2] dark:border-[#3C4768] shadow-sm rounded-lg flex flex-col items-center justify-center transition-transform"
              >
                <span className="text-xs font-bold text-[#171A33] dark:text-[#F4F6FF]">
                  {item.page_num}
                </span>
                {item.duplicate_count > 1 && (
                  <span className="text-[9px] px-1 bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#7568F2] rounded font-semibold mt-1">
                    x{item.duplicate_count}
                  </span>
                )}
              </div>

              {item.deleted && (
                <div className="absolute inset-0 bg-[#FEF3F2]/80 dark:bg-[#401C21]/80 flex items-center justify-center text-xs font-bold text-[#B42318] dark:text-[#FDA29B]">
                  Deleted
                </div>
              )}
            </div>

            {/* Actions Toolbar */}
            <div className="p-2 flex items-center justify-between gap-1 text-[#555D75] dark:text-[#C0C7DC]">
              <button
                type="button"
                onClick={() => movePage(idx, idx - 1)}
                disabled={idx === 0}
                className="p-1 rounded-lg hover:bg-[#EEEDFF] dark:hover:bg-[#29264E] hover:text-[#5146D8] dark:hover:text-[#7568F2] disabled:opacity-20 transition-colors"
                title="Move left"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
              </button>

              <button
                type="button"
                onClick={() => rotatePage(idx)}
                className="p-1 rounded-lg hover:bg-[#EEEDFF] dark:hover:bg-[#29264E] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors"
                title="Rotate 90°"
              >
                <RotateCw className="w-3.5 h-3.5" />
              </button>

              <button
                type="button"
                onClick={() => duplicatePage(idx)}
                className="p-1 rounded-lg hover:bg-[#EEEDFF] dark:hover:bg-[#29264E] hover:text-[#5146D8] dark:hover:text-[#7568F2] transition-colors"
                title="Duplicate"
              >
                <Copy className="w-3.5 h-3.5" />
              </button>

              <button
                type="button"
                onClick={() => toggleDelete(idx)}
                className={`p-1 rounded-lg hover:bg-[#FEF3F2] dark:hover:bg-[#401C21] hover:text-[#B42318] dark:hover:text-[#FDA29B] transition-colors ${
                  item.deleted ? "text-[#B42318] dark:text-[#FDA29B] font-bold" : ""
                }`}
                title="Delete page"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>

              <button
                type="button"
                onClick={() => movePage(idx, idx + 1)}
                disabled={idx === pages.length - 1}
                className="p-1 rounded-lg hover:bg-[#EEEDFF] dark:hover:bg-[#29264E] hover:text-[#5146D8] dark:hover:text-[#7568F2] disabled:opacity-20 transition-colors"
                title="Move right"
              >
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
