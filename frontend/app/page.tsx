import React from "react";
import { Hero } from "@/components/home/Hero";
import { ToolSearch } from "@/components/home/ToolSearch";
import { FeaturedTools } from "@/components/home/FeaturedTools";
import { BrowseByTask } from "@/components/home/BrowseByTask";
import { RecentlyUsed } from "@/components/home/RecentlyUsed";
import { CategorySections } from "@/components/home/CategorySections";
import { SecurityExplainer } from "@/components/home/SecurityExplainer";

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* 1. Hero Section */}
      <Hero />

      {/* 2. Prominent Tool Search */}
      <ToolSearch />

      {/* 3. Popular Tools (8 high-frequency operations) */}
      <FeaturedTools />

      {/* 4. Browse by Task (6 Workflow Categories) */}
      <BrowseByTask />

      {/* 5. Recently Used Tools (Client LocalStorage) */}
      <RecentlyUsed />

      {/* 6. All Categories & Tools */}
      <CategorySections />

      {/* 7. Privacy & Security Architecture */}
      <SecurityExplainer />
    </div>
  );
}
