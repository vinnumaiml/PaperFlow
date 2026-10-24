"use client";

import React, { useRef, useState } from "react";
import { Pen, Type, Upload, Eraser } from "lucide-react";

interface SignPadProps {
  onSignatureReady: (dataUrl: string) => void;
}

export function SignPad({ onSignatureReady }: SignPadProps) {
  const [mode, setMode] = useState<"draw" | "type" | "upload">("draw");
  const [typedName, setTypedName] = useState("");
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);

  // Clear canvas
  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  };

  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    setIsDrawing(true);
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const x = ("touches" in e ? e.touches[0].clientX : e.clientX) - rect.left;
    const y = ("touches" in e ? e.touches[0].clientY : e.clientY) - rect.top;

    ctx.beginPath();
    ctx.moveTo(x, y);
    // Dark mode detection for drawing stroke
    const isDark = document.documentElement.classList.contains("dark");
    ctx.strokeStyle = isDark ? "#F4F6FF" : "#171A33";
    ctx.lineWidth = 2.5;
    ctx.lineCap = "round";
  };

  const draw = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const x = ("touches" in e ? e.touches[0].clientX : e.clientX) - rect.left;
    const y = ("touches" in e ? e.touches[0].clientY : e.clientY) - rect.top;

    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const stopDrawing = () => {
    if (!isDrawing) return;
    setIsDrawing(false);
    const canvas = canvasRef.current;
    if (canvas) {
      onSignatureReady(canvas.toDataURL("image/png"));
    }
  };

  // Convert typed name to canvas signature
  const applyTypedSignature = (name: string) => {
    setTypedName(name);
    if (!name.trim()) return;

    const canvas = document.createElement("canvas");
    canvas.width = 400;
    canvas.height = 120;
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.clearRect(0, 0, 400, 120);
      ctx.font = "italic 36px 'Brush Script MT', 'Dancing Script', cursive, sans-serif";
      const isDark = document.documentElement.classList.contains("dark");
      ctx.fillStyle = isDark ? "#F4F6FF" : "#171A33";
      ctx.fillText(name, 30, 70);
      onSignatureReady(canvas.toDataURL("image/png"));
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === "string") {
        onSignatureReady(reader.result);
      }
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="p-5 rounded-2xl bg-white dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-xs space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-[#5146D8] dark:text-[#7568F2]">
          Create Visual Signature
        </span>

        {/* Mode selector */}
        <div className="flex items-center gap-1 p-1 rounded-xl bg-[#F1F3F9] dark:bg-[#1A2036] border border-[#E2E6F0] dark:border-[#2B3450] text-xs">
          <button
            type="button"
            onClick={() => setMode("draw")}
            className={`flex items-center gap-1 px-3 py-1 rounded-lg font-semibold transition-all ${
              mode === "draw"
                ? "bg-white dark:bg-[#14182B] text-[#5146D8] dark:text-[#7568F2] shadow-xs border border-[#E2E6F0] dark:border-[#2B3450]"
                : "text-[#555D75] dark:text-[#C0C7DC] hover:text-[#171A33] dark:hover:text-[#F4F6FF]"
            }`}
          >
            <Pen className="w-3.5 h-3.5" />
            Draw
          </button>
          <button
            type="button"
            onClick={() => setMode("type")}
            className={`flex items-center gap-1 px-3 py-1 rounded-lg font-semibold transition-all ${
              mode === "type"
                ? "bg-white dark:bg-[#14182B] text-[#5146D8] dark:text-[#7568F2] shadow-xs border border-[#E2E6F0] dark:border-[#2B3450]"
                : "text-[#555D75] dark:text-[#C0C7DC] hover:text-[#171A33] dark:hover:text-[#F4F6FF]"
            }`}
          >
            <Type className="w-3.5 h-3.5" />
            Type
          </button>
          <button
            type="button"
            onClick={() => setMode("upload")}
            className={`flex items-center gap-1 px-3 py-1 rounded-lg font-semibold transition-all ${
              mode === "upload"
                ? "bg-white dark:bg-[#14182B] text-[#5146D8] dark:text-[#7568F2] shadow-xs border border-[#E2E6F0] dark:border-[#2B3450]"
                : "text-[#555D75] dark:text-[#C0C7DC] hover:text-[#171A33] dark:hover:text-[#F4F6FF]"
            }`}
          >
            <Upload className="w-3.5 h-3.5" />
            Upload
          </button>
        </div>
      </div>

      {mode === "draw" && (
        <div className="space-y-2">
          <div className="relative border-2 border-dashed border-[#CCD2E2] dark:border-[#3C4768] rounded-2xl bg-white dark:bg-[#1A2036] overflow-hidden">
            <canvas
              ref={canvasRef}
              width={500}
              height={150}
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseLeave={stopDrawing}
              onTouchStart={startDrawing}
              onTouchMove={draw}
              onTouchEnd={stopDrawing}
              className="w-full h-[150px] cursor-crosshair touch-none"
            />
          </div>
          <button
            type="button"
            onClick={clearCanvas}
            className="flex items-center gap-1 text-xs text-[#555D75] dark:text-[#C0C7DC] hover:text-[#B42318] dark:hover:text-[#FDA29B] transition-colors cursor-pointer"
          >
            <Eraser className="w-3.5 h-3.5" />
            Clear signature
          </button>
        </div>
      )}

      {mode === "type" && (
        <div className="space-y-3">
          <input
            type="text"
            value={typedName}
            onChange={(e) => applyTypedSignature(e.target.value)}
            placeholder="Type your full name..."
            className="w-full px-4 py-2.5 rounded-xl bg-[#F7F8FC] dark:bg-[#1A2036] border border-[#CCD2E2] dark:border-[#3C4768] text-[#171A33] dark:text-[#F4F6FF] placeholder:text-[#788198] text-sm focus:outline-none focus:ring-2 focus:ring-[#A5B4FC]"
          />
          {typedName && (
            <div className="p-4 rounded-xl bg-[#F1F3F9] dark:bg-[#1A2036] border border-[#E2E6F0] dark:border-[#2B3450] flex items-center justify-center">
              <span className="font-serif italic text-3xl text-[#5146D8] dark:text-[#7568F2]">
                {typedName}
              </span>
            </div>
          )}
        </div>
      )}

      {mode === "upload" && (
        <div className="space-y-2">
          <input
            type="file"
            accept="image/png,image/jpeg,image/svg+xml"
            onChange={handleImageUpload}
            className="block w-full text-xs text-[#555D75] dark:text-[#C0C7DC] file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-[#EEEDFF] dark:file:bg-[#29264E] file:text-[#5146D8] dark:file:text-[#7568F2] hover:file:bg-[#CECBFF] cursor-pointer"
          />
        </div>
      )}
    </div>
  );
}
