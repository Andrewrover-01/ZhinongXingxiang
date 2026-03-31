"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ username: "", phone: "", password: "", real_name: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await authApi.register(form);
      await authApi.login({ username: form.username, password: form.password });
      // Token is stored in an httpOnly cookie set by the server — no localStorage needed
      router.push("/farmland");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg ?? "注册失败，请重试");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <div className="text-4xl mb-2">🌾</div>
          <CardTitle>创建账户</CardTitle>
          <CardDescription>加入智农兴乡平台</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <div className="rounded-md bg-destructive/10 text-destructive text-sm px-3 py-2">
                {error}
              </div>
            )}
            <div className="space-y-1">
              <Label htmlFor="username">用户名</Label>
              <Input id="username" name="username" value={form.username} onChange={handleChange} placeholder="3-50个字符" required minLength={3} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="phone">手机号</Label>
              <Input id="phone" name="phone" value={form.phone} onChange={handleChange} placeholder="1开头11位手机号" required pattern="^1[3-9]\d{9}$" />
            </div>
            <div className="space-y-1">
              <Label htmlFor="real_name">姓名（选填）</Label>
              <Input id="real_name" name="real_name" value={form.real_name} onChange={handleChange} placeholder="真实姓名" />
            </div>
            <div className="space-y-1">
              <Label htmlFor="password">密码</Label>
              <Input id="password" name="password" type="password" value={form.password} onChange={handleChange} placeholder="至少6位" required minLength={6} />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col gap-3">
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "注册中..." : "注册"}
            </Button>
            <p className="text-sm text-muted-foreground">
              已有账户？{" "}
              <Link href="/login" className="text-primary hover:underline">
                立即登录
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </main>
  );
}
