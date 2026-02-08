import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/eval/:path*",
        destination: "http://localhost:3201/api/eval/:path*",
      },
    ];
  },
};

export default nextConfig;
