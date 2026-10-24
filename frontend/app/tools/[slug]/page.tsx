import React from "react";
import { notFound } from "next/navigation";
import { Metadata } from "next";
import { TOOLS, getToolBySlug } from "@/lib/tools/registry";
import { ToolPageLayout } from "@/components/tools/ToolPageLayout";

interface ToolPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  return TOOLS.map((tool) => ({
    slug: tool.slug,
  }));
}

export async function generateMetadata({ params }: ToolPageProps): Promise<Metadata> {
  const { slug } = await params;
  const tool = getToolBySlug(slug);
  if (!tool) {
    return {
      title: "Tool Not Found - PaperFlow",
    };
  }

  return {
    title: `${tool.displayName} - Free Online PDF Tool | PaperFlow`,
    description: tool.longDescription,
  };
}

export default async function ToolPage({ params }: ToolPageProps) {
  const { slug } = await params;
  const tool = getToolBySlug(slug);

  if (!tool) {
    notFound();
  }

  return <ToolPageLayout tool={tool} />;
}
