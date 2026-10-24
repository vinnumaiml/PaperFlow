"use client";

import React from "react";
import { formatBytes } from "@/lib/utils/cn";
import { FileText, Trash2, ArrowUp, ArrowDown } from "lucide-react";

interface FileListProps {
  files: File[];
  onRemove: (index: number) => void;
  onReorder?: (newFiles: File[]) => void;
  allowReorder?: boolean;
}

export function FileList({ files, onRemove, onReorder, allowReorder = false }: FileListProps) {
  if (files.length === 0) return null;

  const moveUp = (index: number) => {
    if (index === 0 || !onReorder) return;
    const copy = [...files];
    const temp = copy[index - 1];
    copy[index - 1] = copy[index];
    copy[index] = temp;
    onReorder(copy);
  };

  const moveDown = (index: number) => {
    if (index === files.length - 1 || !onReorder) return;
    const copy = [...files];
    const temp = copy[index + 1];
    copy[index + 1] = copy[index];
    copy[index] = temp;
    onReorder(copy);
  };

  return (
    <div className="w-full space-y-2 mt-4">
      <div className="flex items-center justify-between text-xs font-semibold text-[#788198] dark:text-[#939DB8] uppercase px-1">
        <span>Selected Files ({files.length})</span>
        {allowReorder && files.length > 1 && (
          <span className="text-[11px] font-normal text-[#5146D8] dark:text-[#7568F2]">
            Reorder using arrows
          </span>
        )}
      </div>

      <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
        {files.map((file, idx) => (
          <div
            key={`${file.name}-${idx}`}
            className="flex items-center justify-between gap-3 p-3 rounded-xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs"
          >
            <div className="flex items-center gap-3 min-w-0">
              {allowReorder && files.length > 1 && (
                <div className="flex flex-col gap-0.5 text-[#788198] dark:text-[#939DB8]">
                  <button
                    type="button"
                    disabled={idx === 0}
                    onClick={() => moveUp(idx)}
                    className="p-1 rounded hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] disabled:opacity-30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A5B4FC]"
                  >
                    <ArrowUp className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    disabled={idx === files.length - 1}
                    onClick={() => moveDown(idx)}
                    className="p-1 rounded hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] disabled:opacity-30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A5B4FC]"
                  >
                    <ArrowDown className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}

              <div className="w-9 h-9 rounded-lg bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#7568F2] flex items-center justify-center shrink-0">
                <FileText className="w-4 h-4" />
              </div>

              <div className="min-w-0">
                <h5 className="text-xs font-bold text-[#171A33] dark:text-[#F4F6FF] truncate">
                  {file.name}
                </h5>
                <p className="text-[11px] text-[#788198] dark:text-[#939DB8]">{formatBytes(file.size)}</p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => onRemove(idx)}
              className="p-2 rounded-lg text-[#788198] hover:text-[#B42318] hover:bg-[#FEF3F2] dark:hover:text-[#FDA29B] dark:hover:bg-[#401C21] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A5B4FC]"
              title="Remove file"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
