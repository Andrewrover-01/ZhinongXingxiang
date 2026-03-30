import type { NextConfig } from "next";

// Set NEXT_PUBLIC_CAPACITOR=true when building the static export for Capacitor APK.
// Normal Docker / server builds leave this unset and use `standalone` output.
const isCapacitorBuild = process.env.NEXT_PUBLIC_CAPACITOR === "true";

const SECURITY_HEADERS = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "SAMEORIGIN" },
  { key: "X-XSS-Protection", value: "1; mode=block" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=()",
  },
];

const nextConfig: NextConfig = {
  // `standalone` for Docker/server deployment; `export` for Capacitor APK
  output: isCapacitorBuild ? "export" : "standalone",
  images: {
    // Static export requires unoptimized images (no Next.js image server)
    unoptimized: isCapacitorBuild,
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
      },
    ],
  },
  // Security headers are only applied in server mode (not static export)
  ...(isCapacitorBuild
    ? {}
    : {
        async headers() {
          return [
            {
              source: "/(.*)",
              headers: SECURITY_HEADERS,
            },
          ];
        },
      }),
};

export default nextConfig;
