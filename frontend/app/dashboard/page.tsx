"use client";

import { useQuery } from "@tanstack/react-query";
import { farmlandApi, aiDoctorApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Nav } from "@/components/nav";
import { Sprout, MapPin, TrendingUp, Activity } from "lucide-react";

// ── Simple bar chart with pure CSS ───────────────────────────────────────────
function BarChart({
  data,
  maxVal,
  color = "bg-primary",
}: {
  data: { label: string; value: number }[];
  maxVal: number;
  color?: string;
}) {
  return (
    <div className="flex items-end gap-1.5 h-28">
      {data.map((d) => (
        <div key={d.label} className="flex flex-col items-center gap-1 flex-1">
          <span className="text-[10px] text-muted-foreground">{d.value}</span>
          <div
            className={`${color} rounded-t-sm w-full transition-all`}
            style={{ height: maxVal > 0 ? `${(d.value / maxVal) * 80}px` : "2px" }}
          />
          <span className="text-[10px] text-muted-foreground">{d.label}</span>
        </div>
      ))}
    </div>
  );
}

// ── Stat card ────────────────────────────────────────────────────────────────
function StatCard({
  icon,
  label,
  value,
  sub,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <Card>
      <CardContent className="pt-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{label}</p>
            <p className="text-2xl font-bold mt-1">{value}</p>
            {sub && <p className="text-xs text-muted-foreground mt-0.5">{sub}</p>}
          </div>
          <div className="text-muted-foreground/60">{icon}</div>
        </div>
      </CardContent>
    </Card>
  );
}

// ── Progress bar ──────────────────────────────────────────────────────────────
function ProgressRow({
  label,
  value,
  total,
  color,
}: {
  label: string;
  value: number;
  total: number;
  color: string;
}) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span>{label}</span>
        <span className="text-muted-foreground">
          {value} 块 ({pct}%)
        </span>
      </div>
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { data: farmlands = [] } = useQuery({
    queryKey: ["farmlands"],
    queryFn: farmlandApi.list,
  });

  const { data: records = [] } = useQuery({
    queryKey: ["ai-doctor-records"],
    queryFn: () => aiDoctorApi.records(0, 100),
  });

  // ── Compute stats ──────────────────────────────────────────────────────────
  const totalArea = farmlands.reduce((s, f) => s + parseFloat(f.area || "0"), 0);

  const cropCounts: Record<string, number> = {};
  for (const f of farmlands) {
    const c = f.crop_type || "未知";
    cropCounts[c] = (cropCounts[c] ?? 0) + 1;
  }
  const topCrops = Object.entries(cropCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
  const maxCropCount = topCrops[0]?.[1] ?? 0;

  // Severity distribution from diagnosis records
  const severityCounts: Record<string, number> = { mild: 0, moderate: 0, severe: 0 };
  for (const r of records) {
    if (r.severity && r.severity in severityCounts) {
      severityCounts[r.severity] += 1;
    }
  }

  // Monthly diagnosis trend (last 6 months)
  const now = new Date();
  const monthlyData: { label: string; value: number }[] = [];
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const label = `${d.getMonth() + 1}月`;
    const count = records.filter((r) => {
      const rd = new Date(r.created_at);
      return rd.getFullYear() === d.getFullYear() && rd.getMonth() === d.getMonth();
    }).length;
    monthlyData.push({ label, value: count });
  }
  const maxMonthly = Math.max(...monthlyData.map((d) => d.value), 1);

  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main className="mx-auto max-w-5xl px-4 py-6 space-y-6">
        <h1 className="text-xl font-bold">📊 数据看板</h1>

        {/* Stat cards row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard
            icon={<Sprout className="h-8 w-8" />}
            label="农田总数"
            value={farmlands.length}
            sub="块地"
          />
          <StatCard
            icon={<MapPin className="h-8 w-8" />}
            label="总面积"
            value={totalArea.toFixed(1)}
            sub="亩"
          />
          <StatCard
            icon={<Activity className="h-8 w-8" />}
            label="诊断次数"
            value={records.length}
            sub="累计"
          />
          <StatCard
            icon={<TrendingUp className="h-8 w-8" />}
            label="本月诊断"
            value={monthlyData[5]?.value ?? 0}
            sub="次"
          />
        </div>

        {/* Charts row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Monthly diagnosis trend */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">病虫害诊断月度趋势</CardTitle>
            </CardHeader>
            <CardContent>
              {records.length === 0 ? (
                <div className="h-28 flex items-center justify-center text-muted-foreground text-sm">
                  暂无诊断数据
                </div>
              ) : (
                <BarChart data={monthlyData} maxVal={maxMonthly} color="bg-primary" />
              )}
            </CardContent>
          </Card>

          {/* Crop distribution */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">作物种类分布</CardTitle>
            </CardHeader>
            <CardContent>
              {topCrops.length === 0 ? (
                <div className="h-28 flex items-center justify-center text-muted-foreground text-sm">
                  暂无农田数据
                </div>
              ) : (
                <BarChart
                  data={topCrops.map(([label, value]) => ({ label, value }))}
                  maxVal={maxCropCount}
                  color="bg-green-500"
                />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Diagnosis severity breakdown */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">病虫害严重程度分布</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {records.length === 0 ? (
              <p className="text-sm text-muted-foreground">暂无诊断记录</p>
            ) : (
              <>
                <ProgressRow
                  label="🟢 轻度"
                  value={severityCounts.mild}
                  total={records.length}
                  color="bg-green-400"
                />
                <ProgressRow
                  label="🟡 中度"
                  value={severityCounts.moderate}
                  total={records.length}
                  color="bg-yellow-400"
                />
                <ProgressRow
                  label="🔴 重度"
                  value={severityCounts.severe}
                  total={records.length}
                  color="bg-red-500"
                />
              </>
            )}
          </CardContent>
        </Card>

        {/* Farmland list overview */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">农田概览</CardTitle>
          </CardHeader>
          <CardContent>
            {farmlands.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                暂无农田数据，请先前往{" "}
                <a href="/farmland" className="text-primary hover:underline">
                  农田管理
                </a>{" "}
                页面添加农田
              </p>
            ) : (
              <div className="divide-y">
                {farmlands.map((f) => (
                  <div
                    key={f.id}
                    className="flex items-center justify-between py-2 text-sm"
                  >
                    <div>
                      <span className="font-medium">{f.name}</span>
                      {f.location && (
                        <span className="text-muted-foreground ml-2 text-xs">
                          📍 {f.location}
                        </span>
                      )}
                    </div>
                    <div className="text-right text-xs text-muted-foreground">
                      <p>{f.area} 亩</p>
                      {f.crop_type && <p>{f.crop_type}</p>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
