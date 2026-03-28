import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-8 p-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-primary mb-2">🌾 智农兴乡</h1>
        <p className="text-muted-foreground text-lg">基于 RAG 的智慧农业全栈平台</p>
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 w-full max-w-2xl">
        {[
          { icon: "🩺", label: "AI 医生", href: "/ai-doctor", desc: "病虫害智能诊断" },
          { icon: "📋", label: "农策助手", href: "/policy", desc: "政策问答咨询" },
          { icon: "📊", label: "数据看板", href: "/dashboard", desc: "农情可视化" },
          { icon: "🤖", label: "农事 Agent", href: "/agent", desc: "智能农事规划" },
        ].map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex flex-col items-center gap-2 rounded-xl border bg-card p-6 shadow-sm hover:shadow-md hover:border-primary transition-all"
          >
            <span className="text-4xl">{item.icon}</span>
            <span className="font-semibold">{item.label}</span>
            <span className="text-xs text-muted-foreground text-center">{item.desc}</span>
          </Link>
        ))}
      </div>
      <div className="flex gap-4">
        <Link
          href="/login"
          className="rounded-md bg-primary px-6 py-2 text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          登录
        </Link>
        <Link
          href="/register"
          className="rounded-md border px-6 py-2 hover:bg-accent transition-colors"
        >
          注册
        </Link>
        <Link
          href="/farmland"
          className="rounded-md border border-primary text-primary px-6 py-2 hover:bg-primary/10 transition-colors"
        >
          我的农田
        </Link>
      </div>
    </main>
  );
}
