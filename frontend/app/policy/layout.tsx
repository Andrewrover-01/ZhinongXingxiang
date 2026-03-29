import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "农策助手",
  description: "基于 RAG 的农业政策问答系统，精准解读种粮补贴、农机购置、农业保险等惠农政策。",
};

export default function PolicyLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
