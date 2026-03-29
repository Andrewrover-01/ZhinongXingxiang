import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "农事 Agent",
  description: "AI 智能农事规划 Agent，根据农田状况自动制定施肥、灌溉、病虫害防治等农事计划。",
};

export default function AgentLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
