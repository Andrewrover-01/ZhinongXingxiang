"use client";

import { useState, useRef, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Upload,
  Camera,
  Loader2,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Clock,
} from "lucide-react";
import {
  aiDoctorApi,
  farmlandApi,
  uploadApi,
  streamDiagnose,
  DiagnoseResponse,
  DiagnoseRecord,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Nav } from "@/components/nav";
import { cn } from "@/lib/utils";
import { captureImage, isNative } from "@/lib/camera";

// ── Severity helpers ──────────────────────────────────────────────────────────
const SEVERITY_MAP: Record<string, { label: string; color: string; bars: number }> = {
  mild: { label: "轻度", color: "success", bars: 1 },
  moderate: { label: "中度", color: "warning", bars: 2 },
  severe: { label: "重度", color: "destructive", bars: 3 },
};

function SeverityBar({ severity }: { severity?: string }) {
  if (!severity) return null;
  const info = SEVERITY_MAP[severity] ?? { label: severity, color: "outline", bars: 0 };
  return (
    <div className="flex items-center gap-2">
      <Badge variant={info.color as "success" | "warning" | "destructive" | "outline"}>
        {info.label}
      </Badge>
      <div className="flex gap-0.5">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className={cn(
              "h-3 w-6 rounded-sm",
              i <= info.bars
                ? info.bars === 3
                  ? "bg-destructive"
                  : info.bars === 2
                  ? "bg-yellow-400"
                  : "bg-green-400"
                : "bg-muted"
            )}
          />
        ))}
      </div>
    </div>
  );
}

// ── Diagnosis Result Card ─────────────────────────────────────────────────────
function DiagnosisCard({
  result,
  streaming,
  streamText,
}: {
  result?: DiagnoseResponse;
  streaming: boolean;
  streamText: string;
}) {
  const [showSources, setShowSources] = useState(false);

  if (!result && !streaming && !streamText) return null;

  if (streaming || (!result && streamText)) {
    return (
      <Card className="mt-4 border-primary/40">
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            正在诊断中…
          </CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="whitespace-pre-wrap text-sm text-foreground/80 font-sans leading-relaxed">
            {streamText}
            <span className="inline-block w-1 h-4 bg-primary animate-pulse ml-0.5 align-middle" />
          </pre>
        </CardContent>
      </Card>
    );
  }

  if (!result) return null;

  return (
    <Card className="mt-4 border-green-400/50">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-base flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-orange-500" />
            {result.diagnosis}
          </CardTitle>
          {result.confidence != null && (
            <span className="text-xs text-muted-foreground shrink-0">
              置信度 {(result.confidence * 100).toFixed(1)}%
            </span>
          )}
        </div>
        <SeverityBar severity={result.severity} />
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <div>
          <p className="font-medium mb-1">🛡️ 防治方案</p>
          <pre className="whitespace-pre-wrap text-foreground/80 font-sans leading-relaxed">
            {result.treatment_plan}
          </pre>
        </div>
        {result.medicine_suggest && (
          <div>
            <p className="font-medium mb-1">💊 推荐药品</p>
            <p className="text-foreground/80">{result.medicine_suggest}</p>
          </div>
        )}
        {result.sources.length > 0 && (
          <div className="border-t pt-2">
            <button
              onClick={() => setShowSources((v) => !v)}
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
            >
              📚 参考来源 ({result.sources.length})
              {showSources ? (
                <ChevronUp className="h-3 w-3" />
              ) : (
                <ChevronDown className="h-3 w-3" />
              )}
            </button>
            {showSources && (
              <ul className="mt-2 space-y-1.5">
                {result.sources.map((s) => (
                  <li key={s.id} className="text-xs text-muted-foreground bg-muted rounded px-2 py-1.5">
                    <p className="font-medium text-foreground/70">{s.title}</p>
                    <p className="line-clamp-2">{s.snippet}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ── History Record Row ────────────────────────────────────────────────────────
function RecordRow({ rec }: { rec: DiagnoseRecord }) {
  const [open, setOpen] = useState(false);
  const sev = rec.severity ? SEVERITY_MAP[rec.severity] : null;
  return (
    <div className="border rounded-lg overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-accent transition-colors"
        onClick={() => setOpen((v) => !v)}
      >
        <div className="flex items-center gap-3 min-w-0">
          {rec.image_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={rec.image_url}
              alt=""
              className="h-10 w-10 rounded object-cover shrink-0 bg-muted"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none";
              }}
            />
          )}
          <div className="min-w-0">
            <p className="font-medium truncate text-sm">{rec.diagnosis || "诊断结果"}</p>
            <p className="text-xs text-muted-foreground">
              {rec.crop_type && `${rec.crop_type} · `}
              {new Date(rec.created_at).toLocaleDateString("zh-CN")}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {sev && (
            <Badge variant={sev.color as "success" | "warning" | "destructive"}>
              {sev.label}
            </Badge>
          )}
          {open ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </div>
      </button>
      {open && (
        <div className="px-4 py-3 border-t text-sm space-y-2 bg-muted/30">
          {rec.description && <p className="text-muted-foreground">{rec.description}</p>}
          <div>
            <p className="font-medium">🛡️ 防治方案</p>
            <pre className="whitespace-pre-wrap text-foreground/80 font-sans text-xs leading-relaxed mt-1">
              {rec.treatment_plan}
            </pre>
          </div>
          {rec.medicine_suggest && (
            <p>
              <span className="font-medium">💊 推荐药品：</span>
              {rec.medicine_suggest}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function AiDoctorPage() {
  const [imageUrl, setImageUrl] = useState("");
  const [previewUrl, setPreviewUrl] = useState("");
  const [description, setDescription] = useState("");
  const [cropType, setCropType] = useState("");
  const [farmlandId, setFarmlandId] = useState("");
  const [uploading, setUploading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [streamText, setStreamText] = useState("");
  const [result, setResult] = useState<DiagnoseResponse | null>(null);
  const [error, setError] = useState("");
  const [tab, setTab] = useState<"diagnose" | "history">("diagnose");
  const fileRef = useRef<HTMLInputElement>(null);

  const { data: farmlands = [] } = useQuery({
    queryKey: ["farmlands"],
    queryFn: farmlandApi.list,
  });

  const { data: records = [], refetch: refetchRecords } = useQuery({
    queryKey: ["ai-doctor-records"],
    queryFn: () => aiDoctorApi.records(),
    enabled: tab === "history",
  });

  const uploadFile = useCallback(async (file: Blob, filename = "image.jpg") => {
    setUploading(true);
    setError("");
    try {
      const res = await uploadApi.upload(new File([file], filename, { type: file.type || "image/jpeg" }));
      setImageUrl(res.url);
    } catch {
      setError("图片上传失败，请重试");
    } finally {
      setUploading(false);
    }
  }, []);

  const handleFileChange = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    // Preview
    setPreviewUrl(URL.createObjectURL(file));
    await uploadFile(file, file.name);
  }, [uploadFile]);

  /** Called when the user taps the camera/upload area */
  const handleCameraClick = useCallback(async () => {
    if (isNative()) {
      // On Android/iOS: open native camera or picker
      const result = await captureImage("camera");
      if (result) {
        setPreviewUrl(result.previewUrl);
        await uploadFile(result.blob, "capture.jpg");
      }
    } else {
      // Browser: trigger the hidden file input
      fileRef.current?.click();
    }
  }, [uploadFile]);

  /** Native gallery picker — only shown in Capacitor */
  const handleGalleryClick = useCallback(async () => {
    const result = await captureImage("gallery");
    if (result) {
      setPreviewUrl(result.previewUrl);
      await uploadFile(result.blob, "gallery.jpg");
    }
  }, [uploadFile]);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      const file = e.dataTransfer.files?.[0];
      if (file) {
        const input = fileRef.current;
        if (input) {
          const dt = new DataTransfer();
          dt.items.add(file);
          input.files = dt.files;
          input.dispatchEvent(new Event("change", { bubbles: true }));
        }
      }
    },
    []
  );

  async function handleDiagnose(e: React.FormEvent) {
    e.preventDefault();
    if (!imageUrl && !previewUrl) {
      setError("请先上传图片");
      return;
    }
    setError("");
    setResult(null);
    setStreamText("");
    setStreaming(true);

    const token =
      typeof window !== "undefined" ? localStorage.getItem("access_token") ?? "" : "";

    const payload = {
      image_url: imageUrl || previewUrl || "https://example.com/placeholder.jpg",
      description: description || undefined,
      crop_type: cropType || undefined,
      farmland_id: farmlandId || undefined,
    };

    try {
      // Try streaming first
      const reader = streamDiagnose(payload, token);
      const decoder = new TextDecoder();
      let accumulated = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        // Parse SSE: "data: ...\n\n"
        const lines = chunk.split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6).trim();
            if (data === "[DONE]") break;
            accumulated += data;
            setStreamText(accumulated);
          }
        }
      }
      setStreaming(false);

      // After stream ends, fetch the persisted record via regular diagnose to get structured data
      const r = await aiDoctorApi.diagnose(payload);
      setResult(r);
      setStreamText("");
    } catch {
      setStreaming(false);
      // Fallback: non-streaming diagnose
      try {
        const r = await aiDoctorApi.diagnose(payload);
        setResult(r);
      } catch (err2: unknown) {
        const msg = (err2 as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail;
        setError(msg ?? "诊断失败，请重试");
      }
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main className="mx-auto max-w-2xl px-4 py-6">
        {/* Tab bar */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setTab("diagnose")}
            className={cn(
              "flex-1 rounded-lg py-2.5 text-sm font-medium transition-colors",
              tab === "diagnose"
                ? "bg-primary text-primary-foreground"
                : "border hover:bg-accent text-muted-foreground"
            )}
          >
            🩺 开始诊断
          </button>
          <button
            onClick={() => {
              setTab("history");
              refetchRecords();
            }}
            className={cn(
              "flex-1 rounded-lg py-2.5 text-sm font-medium transition-colors",
              tab === "history"
                ? "bg-primary text-primary-foreground"
                : "border hover:bg-accent text-muted-foreground"
            )}
          >
            <Clock className="h-4 w-4 inline mr-1" />
            历史记录
          </button>
        </div>

        {/* Diagnose Tab */}
        {tab === "diagnose" && (
          <form onSubmit={handleDiagnose} className="space-y-4">
            {/* Image Upload */}
            <div
              className={cn(
                "border-2 border-dashed rounded-xl flex flex-col items-center justify-center gap-3 p-8 cursor-pointer transition-colors hover:border-primary hover:bg-primary/5",
                previewUrl ? "border-primary/40" : "border-muted-foreground/30"
              )}
              onClick={handleCameraClick}
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              role="button"
              aria-label="上传或拍摄病害图片"
              tabIndex={0}
              onKeyDown={(e) => e.key === "Enter" && handleCameraClick()}
            >
              {previewUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={previewUrl}
                  alt="预览"
                  className="max-h-48 rounded-lg object-contain"
                />
              ) : (
                <>
                  <div className="flex gap-4 text-muted-foreground">
                    <Camera className="h-8 w-8" aria-hidden="true" />
                    <Upload className="h-8 w-8" aria-hidden="true" />
                  </div>
                  <div className="text-center">
                    <p className="font-medium text-sm">
                      {isNative() ? "点击拍照" : "点击或拖拽上传图片"}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      支持 JPG、PNG 格式
                    </p>
                  </div>
                </>
              )}
              {uploading && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                  上传中…
                </div>
              )}
            </div>
            {/* Native gallery button — only visible in Capacitor app */}
            {isNative() && (
              <Button
                type="button"
                variant="outline"
                className="w-full"
                onClick={handleGalleryClick}
                disabled={uploading}
              >
                <Upload className="h-4 w-4 mr-2" aria-hidden="true" />
                从相册选取
              </Button>
            )}
            {/* Hidden file input — used in browser / PWA */}
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              capture="environment"
              className="hidden"
              onChange={handleFileChange}
            />

            {/* Or paste URL */}
            <div className="space-y-1">
              <Label htmlFor="img-url">或粘贴图片 URL</Label>
              <Input
                id="img-url"
                placeholder="https://..."
                value={imageUrl}
                onChange={(e) => {
                  setImageUrl(e.target.value);
                  setPreviewUrl(e.target.value);
                }}
              />
            </div>

            {/* Description */}
            <div className="space-y-1">
              <Label htmlFor="desc">描述症状（可选）</Label>
              <Textarea
                id="desc"
                rows={3}
                placeholder="例：叶片发黄，出现褐色斑点，边缘有水渍状晕圈…"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {/* Crop type + farmland */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label htmlFor="crop">作物种类</Label>
                <Input
                  id="crop"
                  placeholder="例：水稻"
                  value={cropType}
                  onChange={(e) => setCropType(e.target.value)}
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="farmland">关联农田</Label>
                <select
                  id="farmland"
                  value={farmlandId}
                  onChange={(e) => setFarmlandId(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <option value="">请选择（可选）</option>
                  {farmlands.map((f) => (
                    <option key={f.id} value={f.id}>
                      {f.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {error && (
              <div className="rounded-md bg-destructive/10 text-destructive text-sm px-3 py-2">
                {error}
              </div>
            )}

            <Button
              type="submit"
              className="w-full"
              size="lg"
              disabled={streaming || uploading}
            >
              {streaming ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  诊断中…
                </>
              ) : (
                "🔍 开始诊断"
              )}
            </Button>
          </form>
        )}

        {/* Diagnosis Result */}
        {tab === "diagnose" && (
          <DiagnosisCard result={result ?? undefined} streaming={streaming} streamText={streamText} />
        )}

        {/* History Tab */}
        {tab === "history" && (
          <div className="space-y-3">
            {records.length === 0 && (
              <div className="text-center py-16 text-muted-foreground">
                <p className="text-4xl mb-3">🔬</p>
                <p>暂无诊断记录</p>
              </div>
            )}
            {records.map((r) => (
              <RecordRow key={r.record_id} rec={r} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
