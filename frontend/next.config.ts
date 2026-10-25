import type { NextConfig } from "next";

const isExport =
  process.env.NEXT_EXPORT === "true" ||
  process.env.NETLIFY === "true" ||
  Boolean(process.env.GITHUB_ACTIONS);
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || undefined;

const nextConfig: NextConfig = {
  output: isExport ? "export" : undefined,
  basePath: basePath,
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  ...(isExport
    ? {}
    : {
        cacheComponents: true,
        partialPrefetching: true,
      }),
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
