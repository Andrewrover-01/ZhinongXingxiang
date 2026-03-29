"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { Sprout, LogOut, Home } from "lucide-react";
import { Button } from "@/components/ui/button";

const NAV_ITEMS = [
  { href: "/ai-doctor", label: "🩺 AI 医生" },
  { href: "/policy", label: "📋 农策助手" },
  { href: "/dashboard", label: "📊 看板" },
  { href: "/farmland", label: "🌱 农田" },
  { href: "/agent", label: "🤖 农事 Agent" },
];

export function Nav() {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
    }
    router.push("/login");
  }

  return (
    <header className="sticky top-0 z-40 border-b bg-card shadow-sm">
      <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-3">
        <Link href="/" className="flex items-center gap-2 font-bold text-primary shrink-0">
          <Sprout className="h-5 w-5" />
          <span className="hidden sm:inline">智农兴乡</span>
        </Link>

        <nav className="flex items-center gap-1 overflow-x-auto flex-1">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "whitespace-nowrap rounded-md px-3 py-1.5 text-sm transition-colors hover:bg-accent",
                pathname?.startsWith(item.href)
                  ? "bg-accent font-medium text-accent-foreground"
                  : "text-muted-foreground"
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2 shrink-0">
          <Link href="/">
            <Button variant="ghost" size="icon" title="首页">
              <Home className="h-4 w-4" />
            </Button>
          </Link>
          <Button variant="ghost" size="icon" title="退出登录" onClick={handleLogout}>
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}
