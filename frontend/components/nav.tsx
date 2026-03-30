"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Sprout, LogOut, Home, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/theme-toggle";

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
  const [menuOpen, setMenuOpen] = useState(false);

  function handleLogout() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
    }
    router.push("/login");
    setMenuOpen(false);
  }

  return (
    <>
      <header className="sticky top-0 z-40 border-b bg-card shadow-sm">
        <div className="mx-auto flex max-w-6xl items-center gap-2 px-4 py-2.5">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 font-bold text-primary shrink-0">
            <Sprout className="h-5 w-5" aria-hidden="true" />
            <span className="hidden sm:inline text-base">智农兴乡</span>
          </Link>

          {/* Desktop nav links */}
          <nav className="hidden sm:flex items-center gap-1 overflow-x-auto flex-1" aria-label="主导航">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                aria-current={pathname?.startsWith(item.href) ? "page" : undefined}
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

          {/* Spacer on mobile */}
          <div className="flex-1 sm:hidden" />

          {/* Right actions */}
          <div className="flex items-center gap-1 shrink-0">
            <ThemeToggle />
            <Link href="/" className="hidden sm:block">
              <Button variant="ghost" size="icon" aria-label="返回首页">
                <Home className="h-4 w-4" aria-hidden="true" />
              </Button>
            </Link>
            <Button
              variant="ghost"
              size="icon"
              aria-label="退出登录"
              onClick={handleLogout}
              className="hidden sm:flex"
            >
              <LogOut className="h-4 w-4" aria-hidden="true" />
            </Button>

            {/* Mobile hamburger */}
            <Button
              variant="ghost"
              size="icon"
              className="sm:hidden"
              onClick={() => setMenuOpen((v) => !v)}
              aria-label={menuOpen ? "关闭菜单" : "打开菜单"}
              aria-expanded={menuOpen}
              aria-controls="mobile-menu"
            >
              {menuOpen ? <X className="h-5 w-5" aria-hidden="true" /> : <Menu className="h-5 w-5" aria-hidden="true" />}
            </Button>
          </div>
        </div>

        {/* Mobile drawer menu */}
        {menuOpen && (
          <div id="mobile-menu" className="sm:hidden border-t bg-card">
            <nav className="flex flex-col divide-y" aria-label="移动端导航">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMenuOpen(false)}
                  aria-current={pathname?.startsWith(item.href) ? "page" : undefined}
                  className={cn(
                    "flex items-center px-4 py-3 text-sm transition-colors",
                    pathname?.startsWith(item.href)
                      ? "bg-accent font-medium text-accent-foreground"
                      : "text-foreground hover:bg-accent"
                  )}
                >
                  {item.label}
                </Link>
              ))}
              <div className="flex items-center justify-between px-4 py-3">
                <Link
                  href="/"
                  onClick={() => setMenuOpen(false)}
                  className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
                >
                  <Home className="h-4 w-4" aria-hidden="true" />
                  首页
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 text-sm text-destructive hover:text-destructive/80"
                >
                  <LogOut className="h-4 w-4" aria-hidden="true" />
                  退出登录
                </button>
              </div>
            </nav>
          </div>
        )}
      </header>
    </>
  );
}
