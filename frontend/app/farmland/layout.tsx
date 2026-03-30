import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "我的农田",
  description: "管理您的农田信息，记录农田位置、面积、作物种类和生长阶段，追踪农业生产情况。",
};

export default function FarmlandLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
