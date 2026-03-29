"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const BOTTOM_ITEMS = [
  { href: "/ai-doctor", icon: "🩺", label: "AI 医生" },
  { href: "/policy", icon: "📋", label: "农策" },
  { href: "/dashboard", icon: "📊", label: "看板" },
  { href: "/farmland", icon: "🌱", label: "农田" },
  { href: "/agent", icon: "🤖", label: "Agent" },
];

export function MobileBottomNav() {
  const pathname = usePathname();
  // Only show on pages that use the Nav (not on auth pages or home)
  const authPaths = ["/login", "/register"];
  if (!pathname || authPaths.includes(pathname) || pathname === "/") return null;

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 sm:hidden border-t bg-card shadow-lg safe-area-bottom">
      <div className="flex">
        {BOTTOM_ITEMS.map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex flex-1 flex-col items-center gap-0.5 py-2 text-center transition-colors",
                active
                  ? "text-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              <span className="text-xl leading-none">{item.icon}</span>
              <span
                className={cn(
                  "text-[10px] leading-tight",
                  active && "font-semibold"
                )}
              >
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
