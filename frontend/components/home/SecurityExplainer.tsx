"use client";

import React from "react";
import { ShieldCheck, Clock, Server, Lock, Sparkles } from "lucide-react";

export function SecurityExplainer() {
  const points = [
    {
      icon: Clock,
      title: "60-Minute Auto-Purge",
      description:
        "Every file uploaded and generated is isolated in a unique job directory and permanently deleted automatically within 60 minutes.",
    },
    {
      icon: Server,
      title: "Isolated Processing Workspaces",
      description:
        "Files never touch shared global folders. Each operation executes inside sandboxed, per-job temporary filesystem paths.",
    },
    {
      icon: Lock,
      title: "Zero Unauthorized Storage",
      description:
        "No account tracking or stealth cloud saving. Document processing runs in-process or in ephemeral server queues.",
    },
    {
      icon: Sparkles,
      title: "Controlled AI Disclosures",
      description:
        "Your documents are never used for AI training. External AI inference is only invoked when you explicitly choose an AI tool.",
    },
  ];

  return (
    <section className="py-16 border-t border-[#E2E6F0] dark:border-[#2B3450] bg-[#F7F8FC] dark:bg-[#0D1020] transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#ECFDF3] dark:bg-[#123528] border border-[#ABEFC6] dark:border-[#24684B] text-[#15803D] dark:text-[#6CE9A6] text-xs font-semibold mb-3">
            <ShieldCheck className="w-4 h-4 text-[#15803D] dark:text-[#6CE9A6]" />
            Security & Data Protection Architecture
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-[#171A33] dark:text-[#F4F6FF] tracking-tight">
            Built for confidentiality and data privacy
          </h2>
          <p className="mt-3 text-xs sm:text-sm text-[#555D75] dark:text-[#C0C7DC]">
            How PaperFlow treats your documents from the moment of upload through automated deletion.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {points.map((p, idx) => {
            const Icon = p.icon;
            return (
              <div
                key={idx}
                className="p-6 rounded-2xl bg-[#FFFFFF] dark:bg-[#14182B] border border-[#E2E6F0] dark:border-[#2B3450] shadow-2xs flex flex-col"
              >
                <div className="w-10 h-10 rounded-xl bg-[#EEEDFF] dark:bg-[#29264E] text-[#5146D8] dark:text-[#7568F2] flex items-center justify-center mb-4">
                  <Icon className="w-5 h-5" />
                </div>
                <h4 className="text-sm font-bold text-[#171A33] dark:text-[#F4F6FF] mb-2">
                  {p.title}
                </h4>
                <p className="text-xs text-[#555D75] dark:text-[#C0C7DC] leading-relaxed flex-1">
                  {p.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
