import React from "react";
import Link from "next/link";
import { Shield } from "lucide-react";

export const metadata = {
  title: "Privacy & Data Retention Policy - PaperFlow",
  description:
    "Learn how PaperFlow protects document privacy through isolated workspaces, strict 60-minute retention, and controlled AI processing.",
};

export default function PrivacyPage() {
  return (
    <div className="py-12 sm:py-16 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#ECFDF3] dark:bg-[#123528] border border-[#ABEFC6] dark:border-[#24684B] text-[#15803D] dark:text-[#6CE9A6] text-xs font-semibold mb-3">
          <Shield className="w-4 h-4 text-[#15803D] dark:text-[#6CE9A6]" />
          Strict Confidentiality
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#171A33] dark:text-[#F4F6FF] tracking-tight">
          Privacy & Data Retention Policy
        </h1>
        <p className="mt-2 text-sm text-[#555D75] dark:text-[#C0C7DC]">
          Last updated: October 2026. This policy describes our exact document handling architecture.
        </p>
      </div>

      <div className="space-y-8 text-sm leading-relaxed text-[#555D75] dark:text-[#C0C7DC]">
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-[#171A33] dark:text-[#F4F6FF]">
            1. Ephemeral, Isolated File Workspaces
          </h2>
          <p>
            When you upload a file to PaperFlow, a randomly generated, cryptographically secure Job ID (UUID v4) is created. All uploaded source documents and generated derivative files reside strictly within that unique isolated workspace directory. Documents are never mixed with other users&apos; files or written to global shared folders.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-[#171A33] dark:text-[#F4F6FF]">
            2. Automatic 60-Minute Retention Policy
          </h2>
          <p>
            PaperFlow operates on a strict, time-bound ephemeral storage model:
          </p>
          <ul className="list-disc pl-5 space-y-1.5">
            <li>Files are kept available only long enough for you to download your results.</li>
            <li>An automated background cleanup engine executes every 15 minutes to purge all workspaces older than 60 minutes.</li>
            <li>You can also immediately trigger deletion at any time by clicking &quot;Cancel/Delete Job&quot; in the interface.</li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-[#171A33] dark:text-[#F4F6FF]">
            3. Explicit AI Feature Disclosure
          </h2>
          <p>
            Unlike many online converters, PaperFlow does not silently route your files to third-party language models or training pipelines:
          </p>
          <ul className="list-disc pl-5 space-y-1.5">
            <li>General document tools (merging, splitting, conversion, compression, editing) run entirely using local Python and binary engines (PyMuPDF, pikepdf, pypdf, ReportLab, openpyxl, python-docx).</li>
            <li>Document content is sent to an external AI provider (such as OpenAI) <strong>only when you explicitly choose</strong> an AI tool (such as AI Summarizer or AI Translator).</li>
            <li>Your documents are never used for model training or retained by PaperFlow for intelligence harvesting.</li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-[#171A33] dark:text-[#F4F6FF]">
            4. Deep Redaction Guarantee
          </h2>
          <p>
            Our Redact PDF tool applies genuine, irreversible stream purging via PyMuPDF&apos;s deep redaction API. Unlike simple visual markup tools that only place black rectangles on top of existing layers, PaperFlow physically removes the underlying text glyphs, font dictionaries, and vector paths so the redacted information cannot be copied, searched, or extracted.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-[#171A33] dark:text-[#F4F6FF]">
            5. No Account or Tracking Requirement
          </h2>
          <p>
            PaperFlow does not require registration, passwords, or credit card numbers for standard processing. We do not place tracking cookies or sell usage telemetry to third parties.
          </p>
        </section>
      </div>

      <div className="pt-6 border-t border-[#E9ECF4] dark:border-[#252E47] flex items-center justify-between">
        <Link
          href="/"
          className="text-xs font-semibold text-[#5146D8] dark:text-[#7568F2] hover:underline"
        >
          ← Return to All Tools
        </Link>
        <Link
          href="/terms"
          className="text-xs font-semibold text-[#555D75] dark:text-[#C0C7DC] hover:text-[#171A33] dark:hover:text-[#F4F6FF]"
        >
          Terms of Service →
        </Link>
      </div>
    </div>
  );
}
