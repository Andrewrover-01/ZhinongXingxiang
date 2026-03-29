import type { Metadata } from "next";
import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";

export const metadata: Metadata = {
  title: "首页",
  description: "智农兴乡 — 基于 RAG 的智慧农业全栈平台，提供 AI 病虫害诊断、农业政策问答、农情数据看板等智能服务。",
};

export default function Home() {
  return (
    <main
      id="main-content"
      className="flex min-h-screen flex-col items-center justify-center gap-8 p-6 pb-safe"
    >
      {/* Header bar with theme toggle */}
      <div className="absolute top-0 right-0 p-3">
        <ThemeToggle />
      </div>

      <div className="text-center">
        <h1 className="text-4xl font-bold text-primary mb-2">🌾 智农兴乡</h1>
        <p className="text-muted-foreground">基于 RAG 的智慧农业全栈平台</p>
      </div>

      <div
        className="grid grid-cols-2 gap-4 w-full max-w-sm sm:max-w-2xl sm:grid-cols-4"
        role="list"
        aria-label="功能入口"
      >
        {[
          { icon: "🩺", label: "AI 医生", href: "/ai-doctor", desc: "病虫害智能诊断" },
          { icon: "📋", label: "农策助手", href: "/policy", desc: "政策问答咨询" },
          { icon: "📊", label: "数据看板", href: "/dashboard", desc: "农情可视化" },
          { icon: "🤖", label: "农事 Agent", href: "/agent", desc: "智能农事规划" },
        ].map((item) => (
          <Link
            key={item.href}
            href={item.href}
            role="listitem"
            aria-label={`${item.label}：${item.desc}`}
            className="flex flex-col items-center gap-2 rounded-xl border bg-card p-5 shadow-sm hover:shadow-md hover:border-primary transition-all active:scale-95"
          >
            <span className="text-4xl" aria-hidden="true">{item.icon}</span>
            <span className="font-semibold text-sm">{item.label}</span>
            <span className="text-xs text-muted-foreground text-center">{item.desc}</span>
          </Link>
        ))}
      </div>

      <div className="flex flex-wrap gap-3 justify-center">
        <Link
          href="/login"
          className="rounded-lg bg-primary px-6 py-2.5 text-sm text-primary-foreground hover:bg-primary/90 transition-colors active:scale-95"
        >
          登录
        </Link>
        <Link
          href="/register"
          className="rounded-lg border px-6 py-2.5 text-sm hover:bg-accent transition-colors active:scale-95"
        >
          注册
        </Link>
        <Link
          href="/farmland"
          className="rounded-lg border border-primary text-primary px-6 py-2.5 text-sm hover:bg-primary/10 transition-colors active:scale-95"
        >
          我的农田
        </Link>
      </div>
    </main>
  );
}


