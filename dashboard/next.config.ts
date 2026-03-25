import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Removed static rewrites block.
  // API proxying is now handled dynamically entirely by middleware.ts at runtime
  // avoiding hardcoded URL issues in Docker containers.
  output: "standalone",
};

export default nextConfig;
