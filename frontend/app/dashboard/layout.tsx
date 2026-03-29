import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "数据看板",
  description: "农情可视化看板，展示农田面积统计、病虫害诊断趋势、作物分布等核心农业数据。",
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
