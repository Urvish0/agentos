import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /**
   * Proxy all /api/* requests to the AgentOS backend.
   * This avoids CORS issues during local development.
   *
   * Example: GET /api/agents/ → http://localhost:8000/agents/
   */
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/:path*",
      },
    ];
  },
};

export default nextConfig;
