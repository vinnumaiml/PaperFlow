"use client";

import React, { useRef, useState } from "react";
import { UploadCloud, Camera, AlertCircle } from "lucide-react";

interface DropZoneProps {
  onFilesSelected: (files: File[]) => void;
  acceptedFormats: string[];
  multiple?: boolean;
  maxSizeMB?: number;
  allowCamera?: boolean;
}

export function DropZone({
  onFilesSelected,
  acceptedFormats,
  multiple = false,
  maxSizeMB = 50,
  allowCamera = false,
}: DropZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const validateAndAddFiles = (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    setError(null);

    const validFiles: File[] = [];
    for (let i = 0; i < fileList.length; i++) {
      const f = fileList[i];
      // Size check
      if (f.size > maxSizeMB * 1024 * 1024) {
        setError(`File "${f.name}" exceeds maximum allowed size of ${maxSizeMB}MB.`);
        return;
      }
      validFiles.push(f);
      if (!multiple) break;
    }

    if (validFiles.length > 0) {
      onFilesSelected(validFiles);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    validateAndAddFiles(e.dataTransfer.files);
  };

  return (
    <div className="w-full">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative flex flex-col items-center justify-center p-8 sm:p-12 rounded-3xl border-2 border-dashed cursor-pointer transition-all duration-150 ${
          isDragOver
            ? "border-[#5146D8] dark:border-[#7568F2] bg-[#EEEDFF] dark:bg-[#29264E] scale-[1.01]"
            : "border-[#CCD2E2] dark:border-[#3C4768] bg-[#FFFFFF] dark:bg-[#14182B] hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] hover:border-[#5146D8] dark:hover:border-[#7568F2]"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedFormats.join(",")}
          multiple={multiple}
          onChange={(e) => validateAndAddFiles(e.target.files)}
          className="hidden"
        />

        {allowCamera && (
          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={(e) => validateAndAddFiles(e.target.files)}
            className="hidden"
          />
        )}

        <div className="w-16 h-16 rounded-2xl bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#7568F2] flex items-center justify-center mb-4 transition-transform group-hover:scale-105">
          <UploadCloud className="w-8 h-8" />
        </div>

        <h3 className="text-base sm:text-lg font-bold text-[#171A33] dark:text-[#F4F6FF] text-center">
          Choose {multiple ? "files" : "file"} or drag & drop here
        </h3>

        <p className="text-xs text-[#788198] dark:text-[#939DB8] text-center mt-1.5 max-w-sm">
          Accepts {acceptedFormats.join(", ")} up to {maxSizeMB}MB
        </p>

        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            className="px-5 py-2.5 rounded-xl bg-[#5146D8] hover:bg-[#4338B8] dark:bg-[#7568F2] dark:hover:bg-[#887DFB] text-white text-xs font-semibold shadow-sm transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A5B4FC]"
          >
            Select from Device
          </button>

          {allowCamera && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                cameraInputRef.current?.click();
              }}
              className="px-4 py-2.5 rounded-xl bg-transparent hover:bg-[#F1F3F9] dark:hover:bg-[#1A2036] border border-[#E2E6F0] dark:border-[#2B3450] text-[#171A33] dark:text-[#F4F6FF] text-xs font-semibold flex items-center gap-2 transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A5B4FC]"
            >
              <Camera className="w-4 h-4 text-[#5146D8] dark:text-[#7568F2]" />
              <span>Use Camera</span>
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-3 p-3.5 rounded-xl bg-[#FEF3F2] dark:bg-[#401C21] border border-[#FECDCA] dark:border-[#7A2E35] flex items-center gap-2 text-xs text-[#B42318] dark:text-[#FDA29B] font-medium">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
