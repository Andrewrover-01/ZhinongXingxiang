import type { Metadata, Viewport } from "next";
import Script from "next/script";
import "./globals.css";
import { Providers } from "@/components/providers";
import { MobileBottomNav } from "@/components/mobile-bottom-nav";
import { CapacitorInit } from "@/components/capacitor-init";

export const metadata: Metadata = {
  title: {
    default: "智农兴乡",
    template: "%s | 智农兴乡",
  },
  description: "基于 RAG 的智慧农业全栈平台，提供 AI 病虫害诊断、农业政策问答、农情看板等服务。",
  manifest: "/manifest.webmanifest",
  robots: { index: true, follow: true },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "智农兴乡",
  },
  formatDetection: {
    telephone: false,
  },
  openGraph: {
    type: "website",
    title: "智农兴乡",
    description: "基于 RAG 的智慧农业全栈平台",
    siteName: "智农兴乡",
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#16a34a" },
    { media: "(prefers-color-scheme: dark)", color: "#166534" },
  ],
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <head>
        <link rel="apple-touch-icon" href="/icons/icon-192.png" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="mobile-web-app-capable" content="yes" />
      </head>
      <body className="min-h-screen bg-background font-sans antialiased overscroll-none">
        {/* Skip to main content — accessibility */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:left-2 focus:top-2 focus:z-[9999] focus:rounded focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:text-primary-foreground"
        >
          跳转到主内容
        </a>
        <Providers>
          <CapacitorInit />
          {children}
          <MobileBottomNav />
        </Providers>
        {/* Register service worker */}
        <Script id="sw-register" strategy="afterInteractive">
          {`
            if ('serviceWorker' in navigator) {
              window.addEventListener('load', function() {
                navigator.serviceWorker.register('/sw.js').catch(function() {});
              });
            }
          `}
        </Script>
      </body>
    </html>
  );
}
