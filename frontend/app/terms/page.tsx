import React from "react";
import Link from "next/link";
import { FileText } from "lucide-react";

export const metadata = {
  title: "Terms of Service - PaperFlow",
  description: "Terms and conditions of using PaperFlow online document utilities.",
};

export default function TermsPage() {
  return (
    <div className="py-12 sm:py-16 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#EEEDFF] dark:bg-[#29264E] border border-[#CECBFF] dark:border-[#3C4768] text-[#5146D8] dark:text-[#7568F2] text-xs font-semibold mb-3">
          <FileText className="w-4 h-4 text-[#5146D8] dark:text-[#7568F2]" />
          User Agreement
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#171A33] dark:text-[#F4F6FF] tracking-tight">
          Terms of Service
        </h1>
        <p className="mt-2 text-sm text-[#555D75] dark:text-[#C0C7DC]">
          Last updated: October 2026.
        </p>
      </div>

      <div className="space-y-8 text-sm leading-relaxed text-[#555D75] dark:text-[#C0C7DC]">
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-[#171A33] dark:text-[#F4F6FF]">
            1. Acceptance of Terms
          </h2>
          <p>
            By accessing or using PaperFlow, you agree to comply with and be bound by these Terms of Service. If you do not agree to these terms, please do not use the service.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-[#171A33] dark:text-[#F4F6FF]">
            2. Permitted Use & Document Ownership
          </h2>
          <p>
            You retain 100% intellectual property ownership of all documents, images, and content you upload to PaperFlow. You represent and warrant that you hold all necessary rights and permissions to upload and modify the documents submitted to the platform.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-[#171A33] dark:text-[#F4F6FF]">
            3. Prohibited Uses
          </h2>
          <p>You agree not to use PaperFlow for any unlawful purpose, including:</p>
          <ul className="list-disc pl-5 space-y-1.5">
            <li>Uploading malicious files containing viruses, trojans, or malware.</li>
            <li>Attempting server-side request forgery (SSRF) or arbitrary system file access.</li>
            <li>Attempting unauthorized password cracking or bypassing encryption on files you do not own.</li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-[#171A33] dark:text-[#F4F6FF]">
            4. Service Availability & Disclaimers
          </h2>
          <p>
            PaperFlow is provided &quot;as is&quot; without warranties of any kind. While we make every effort to achieve the highest possible document conversion, compression, and repair fidelity, certain heavily corrupted files or proprietary formatting may not be recoverable.
          </p>
        </section>
      </div>

      <div className="pt-6 border-t border-[#E9ECF4] dark:border-[#252E47]">
        <Link
          href="/"
          className="text-xs font-semibold text-[#5146D8] dark:text-[#7568F2] hover:underline"
        >
          ← Return to All Tools
        </Link>
      </div>
    </div>
  );
}
