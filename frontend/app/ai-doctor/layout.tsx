import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI 医生",
  description: "上传作物图片，AI 智能识别病虫害，提供详细诊断结果和防治建议，支持离线历史记录查看。",
};

export default function AiDoctorLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
