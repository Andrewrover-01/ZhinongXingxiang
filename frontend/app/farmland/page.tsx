"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, MapPin, Sprout, ArrowLeft } from "lucide-react";
import { farmlandApi, FarmlandPayload, FarmlandResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

const EMPTY_FORM: FarmlandPayload = {
  name: "",
  area: "",
  location: "",
  soil_type: "",
  crop_type: "",
  crop_stage: "",
  sowing_date: "",
  notes: "",
};

export default function FarmlandPage() {
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [editTarget, setEditTarget] = useState<FarmlandResponse | null>(null);
  const [form, setForm] = useState<FarmlandPayload>(EMPTY_FORM);
  const [formError, setFormError] = useState("");

  // ── Queries ──────────────────────────────────────────────────────────────
  const {
    data: farmlands = [],
    isLoading,
    isError,
  } = useQuery({ queryKey: ["farmlands"], queryFn: farmlandApi.list });

  // ── Mutations ─────────────────────────────────────────────────────────────
  const createMutation = useMutation({
    mutationFn: (data: FarmlandPayload) => farmlandApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["farmlands"] });
      closeDialog();
    },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setFormError(msg ?? "保存失败，请重试");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<FarmlandPayload> }) =>
      farmlandApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["farmlands"] });
      closeDialog();
    },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setFormError(msg ?? "更新失败，请重试");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => farmlandApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["farmlands"] });
      setDeleteId(null);
    },
  });

  // ── Helpers ───────────────────────────────────────────────────────────────
  function openCreate() {
    setEditTarget(null);
    setForm(EMPTY_FORM);
    setFormError("");
    setDialogOpen(true);
  }

  function openEdit(f: FarmlandResponse) {
    setEditTarget(f);
    setForm({
      name: f.name,
      area: f.area,
      location: f.location ?? "",
      soil_type: f.soil_type ?? "",
      crop_type: f.crop_type ?? "",
      crop_stage: f.crop_stage ?? "",
      sowing_date: f.sowing_date ?? "",
      notes: f.notes ?? "",
    });
    setFormError("");
    setDialogOpen(true);
  }

  function closeDialog() {
    setDialogOpen(false);
    setEditTarget(null);
    setForm(EMPTY_FORM);
    setFormError("");
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setFormError("");
    const payload: FarmlandPayload = {
      ...form,
      location: form.location || undefined,
      soil_type: form.soil_type || undefined,
      crop_type: form.crop_type || undefined,
      crop_stage: form.crop_stage || undefined,
      sowing_date: form.sowing_date || undefined,
      notes: form.notes || undefined,
    };
    if (editTarget) {
      updateMutation.mutate({ id: editTarget.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  }

  const isSaving = createMutation.isPending || updateMutation.isPending;

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card shadow-sm">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-3">
            <Link href="/" className="text-muted-foreground hover:text-foreground">
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <h1 className="text-xl font-bold flex items-center gap-2">
              <Sprout className="h-5 w-5 text-primary" />
              我的农田
            </h1>
          </div>
          <Button onClick={openCreate} size="sm">
            <Plus className="h-4 w-4 mr-1" />
            新增农田
          </Button>
        </div>
      </header>

      {/* Body */}
      <div className="mx-auto max-w-5xl px-4 py-6">
        {isLoading && (
          <div className="flex justify-center py-20 text-muted-foreground">加载中…</div>
        )}

        {isError && (
          <div className="rounded-md bg-destructive/10 text-destructive px-4 py-3 text-sm">
            加载失败，请刷新重试
          </div>
        )}

        {!isLoading && !isError && farmlands.length === 0 && (
          <div className="flex flex-col items-center gap-4 py-20 text-muted-foreground">
            <Sprout className="h-12 w-12 opacity-30" />
            <p>暂无农田，点击右上角「新增农田」开始管理</p>
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {farmlands.map((f) => (
            <Card key={f.id} className="relative flex flex-col">
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{f.name}</CardTitle>
                {f.location && (
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    {f.location}
                  </p>
                )}
              </CardHeader>
              <CardContent className="flex flex-col gap-1 text-sm flex-1">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">面积</span>
                  <span className="font-medium">{f.area} 亩</span>
                </div>
                {f.crop_type && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">作物</span>
                    <span>{f.crop_type}</span>
                  </div>
                )}
                {f.crop_stage && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">生育期</span>
                    <span>{f.crop_stage}</span>
                  </div>
                )}
                {f.soil_type && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">土壤</span>
                    <span>{f.soil_type}</span>
                  </div>
                )}
                {f.sowing_date && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">播种日期</span>
                    <span>{f.sowing_date}</span>
                  </div>
                )}
                {f.notes && (
                  <p className="mt-2 text-xs text-muted-foreground border-t pt-2 line-clamp-2">
                    {f.notes}
                  </p>
                )}
              </CardContent>
              <div className="flex justify-end gap-2 px-6 pb-4">
                <Button variant="outline" size="sm" onClick={() => openEdit(f)}>
                  <Pencil className="h-3 w-3 mr-1" />
                  编辑
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => setDeleteId(f.id)}
                >
                  <Trash2 className="h-3 w-3 mr-1" />
                  删除
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Create / Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogHeader>
          <DialogTitle>{editTarget ? "编辑农田" : "新增农田"}</DialogTitle>
          <DialogDescription>填写地块基本信息</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3 mt-2">
          {formError && (
            <div className="rounded-md bg-destructive/10 text-destructive text-sm px-3 py-2">
              {formError}
            </div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1 col-span-2">
              <Label htmlFor="name">地块名称 *</Label>
              <Input
                id="name"
                name="name"
                value={form.name}
                onChange={handleChange}
                required
                placeholder="例：东头二亩地"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="area">面积（亩）*</Label>
              <Input
                id="area"
                name="area"
                value={form.area}
                onChange={handleChange}
                required
                placeholder="例：2.5"
                type="number"
                step="0.01"
                min="0.01"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="crop_type">作物种类</Label>
              <Input
                id="crop_type"
                name="crop_type"
                value={form.crop_type}
                onChange={handleChange}
                placeholder="例：水稻"
              />
            </div>
            <div className="space-y-1 col-span-2">
              <Label htmlFor="location">地址</Label>
              <Input
                id="location"
                name="location"
                value={form.location}
                onChange={handleChange}
                placeholder="例：湖南省长沙市望城区"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="soil_type">土壤类型</Label>
              <Input
                id="soil_type"
                name="soil_type"
                value={form.soil_type}
                onChange={handleChange}
                placeholder="例：红壤"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="crop_stage">生育期</Label>
              <Input
                id="crop_stage"
                name="crop_stage"
                value={form.crop_stage}
                onChange={handleChange}
                placeholder="例：分蘖期"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="sowing_date">播种日期</Label>
              <Input
                id="sowing_date"
                name="sowing_date"
                type="date"
                value={form.sowing_date}
                onChange={handleChange}
              />
            </div>
            <div className="space-y-1 col-span-2">
              <Label htmlFor="notes">备注</Label>
              <Input
                id="notes"
                name="notes"
                value={form.notes}
                onChange={handleChange}
                placeholder="可选备注信息"
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={closeDialog}>
              取消
            </Button>
            <Button type="submit" disabled={isSaving}>
              {isSaving ? "保存中…" : "保存"}
            </Button>
          </DialogFooter>
        </form>
      </Dialog>

      {/* Delete Confirm Dialog */}
      <Dialog
        open={deleteId !== null}
        onOpenChange={(o) => {
          if (!o) setDeleteId(null);
        }}
      >
        <DialogHeader>
          <DialogTitle>确认删除</DialogTitle>
          <DialogDescription>删除后无法恢复，确定要删除这块农田吗？</DialogDescription>
        </DialogHeader>
        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={() => setDeleteId(null)}>
            取消
          </Button>
          <Button
            variant="destructive"
            onClick={() => deleteId && deleteMutation.mutate(deleteId)}
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? "删除中…" : "确认删除"}
          </Button>
        </DialogFooter>
      </Dialog>
    </main>
  );
}
