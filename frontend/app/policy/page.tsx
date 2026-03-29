"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Send, Loader2, MessageSquare, ChevronDown, ChevronUp } from "lucide-react";
import {
  policyApi,
  streamPolicyChat,
  PolicyMessage,
  PolicySessionSummary,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Nav } from "@/components/nav";
import { cn } from "@/lib/utils";

// ── Quick-question templates ──────────────────────────────────────────────────
const QUICK_QUESTIONS = [
  "种粮直补政策有哪些？怎么申请？",
  "农业保险怎么购买？有哪些补贴？",
  "农村土地流转需要注意什么？",
  "高标准农田建设补贴标准是多少？",
  "秸秆还田补贴政策有哪些？",
  "农机购置补贴如何申请？",
];

function newSessionId() {
  return `sess-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

// ── Source citation card ──────────────────────────────────────────────────────
function SourceList({ sources }: { sources: PolicyMessage["rag_sources"] }) {
  const [open, setOpen] = useState(false);
  if (!sources || sources.length === 0) return null;
  return (
    <div className="mt-1.5">
      <button
        onClick={() => setOpen((v) => !v)}
        className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1"
      >
        📚 来源引用 ({sources.length})
        {open ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
      </button>
      {open && (
        <ul className="mt-1 space-y-1">
          {sources.map((s) => (
            <li
              key={s.id}
              className="text-xs bg-background border rounded p-2"
            >
              <p className="font-medium">{s.title}</p>
              <p className="text-muted-foreground line-clamp-2">{s.snippet}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ── Message bubble ────────────────────────────────────────────────────────────
function MessageBubble({
  msg,
  streaming,
}: {
  msg: PolicyMessage;
  streaming?: boolean;
}) {
  const isUser = msg.role === "user";
  return (
    <div className={cn("flex gap-2", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-sm shrink-0 mt-0.5">
          🌾
        </div>
      )}
      <div className={cn("max-w-[80%]", isUser ? "items-end" : "items-start", "flex flex-col")}>
        <div
          className={cn(
            "rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
            isUser
              ? "bg-primary text-primary-foreground rounded-tr-sm"
              : "bg-muted text-foreground rounded-tl-sm"
          )}
        >
          <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
          {streaming && (
            <span className="inline-block w-1 h-4 bg-current animate-pulse ml-0.5 align-middle" />
          )}
        </div>
        {!isUser && <SourceList sources={msg.rag_sources} />}
        <span className="text-[10px] text-muted-foreground mt-1 px-1">
          {msg.created_at
            ? new Date(msg.created_at).toLocaleTimeString("zh-CN", {
                hour: "2-digit",
                minute: "2-digit",
              })
            : ""}
        </span>
      </div>
      {isUser && (
        <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center text-sm shrink-0 mt-0.5">
          👤
        </div>
      )}
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function PolicyPage() {
  const queryClient = useQueryClient();
  const [currentSessionId, setCurrentSessionId] = useState<string>(() => newSessionId());
  const [messages, setMessages] = useState<PolicyMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { data: sessions = [], refetch: refetchSessions } = useQuery({
    queryKey: ["policy-sessions"],
    queryFn: policyApi.sessions,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => policyApi.deleteSession(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["policy-sessions"] });
      refetchSessions();
    },
  });

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  async function loadSession(sessionId: string) {
    setCurrentSessionId(sessionId);
    try {
      const msgs = await policyApi.sessionMessages(sessionId);
      setMessages(msgs);
    } catch {
      setMessages([]);
    }
  }

  function createNewSession() {
    const id = newSessionId();
    setCurrentSessionId(id);
    setMessages([]);
  }

  const handleSend = useCallback(
    async (text?: string) => {
      const msgText = (text ?? inputText).trim();
      if (!msgText || isStreaming) return;
      setInputText("");

      const token =
        typeof window !== "undefined"
          ? localStorage.getItem("access_token") ?? ""
          : "";

      // Optimistically add user message
      const userMsg: PolicyMessage = {
        id: `temp-${Date.now()}`,
        session_id: currentSessionId,
        role: "user",
        content: msgText,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      // Placeholder assistant message for streaming
      const assistantMsgId = `stream-${Date.now()}`;
      const assistantMsg: PolicyMessage = {
        id: assistantMsgId,
        session_id: currentSessionId,
        role: "assistant",
        content: "",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      setIsStreaming(true);

      try {
        const reader = streamPolicyChat(currentSessionId, msgText, token);
        const decoder = new TextDecoder();
        let accumulated = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6).trim();
              if (data === "[DONE]") break;
              accumulated += data;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId ? { ...m, content: accumulated } : m
                )
              );
            }
          }
        }
      } catch {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsgId
              ? { ...m, content: "⚠️ 连接失败，请重试" }
              : m
          )
        );
      } finally {
        setIsStreaming(false);
        refetchSessions();
      }
    },
    [inputText, isStreaming, currentSessionId, refetchSessions]
  );

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Nav />
      <div className="flex flex-1 overflow-hidden max-w-6xl mx-auto w-full">
        {/* Sidebar */}
        <aside
          className={cn(
            "border-r bg-card flex flex-col transition-all duration-200",
            showSidebar ? "w-64 min-w-[220px]" : "w-0 overflow-hidden"
          )}
        >
          <div className="flex items-center justify-between px-3 py-3 border-b">
            <span className="font-semibold text-sm">会话历史</span>
            <Button size="sm" variant="ghost" onClick={createNewSession}>
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          <ul className="flex-1 overflow-y-auto py-2">
            {sessions.length === 0 && (
              <li className="px-3 py-8 text-center text-xs text-muted-foreground">
                暂无会话
              </li>
            )}
            {sessions.map((s: PolicySessionSummary) => (
              <li key={s.session_id}>
                <button
                  onClick={() => loadSession(s.session_id)}
                  className={cn(
                    "w-full text-left px-3 py-2 rounded-md mx-1 flex items-start justify-between gap-1 hover:bg-accent transition-colors",
                    s.session_id === currentSessionId && "bg-accent"
                  )}
                >
                  <div className="min-w-0">
                    <p className="text-xs font-medium truncate">{s.last_message}</p>
                    <p className="text-[10px] text-muted-foreground">
                      {s.message_count} 条 ·{" "}
                      {new Date(s.last_at).toLocaleDateString("zh-CN")}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteMutation.mutate(s.session_id);
                      if (s.session_id === currentSessionId) createNewSession();
                    }}
                    className="text-muted-foreground hover:text-destructive shrink-0 mt-0.5"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        {/* Chat area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Chat header */}
          <div className="border-b px-4 py-3 flex items-center gap-3">
            <button
              onClick={() => setShowSidebar((v) => !v)}
              className="text-muted-foreground hover:text-foreground"
            >
              <MessageSquare className="h-5 w-5" />
            </button>
            <h1 className="font-semibold">📋 农策助手</h1>
            <span className="text-xs text-muted-foreground ml-auto">
              基于 RAG 的农业政策智能问答
            </span>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
            {messages.length === 0 && (
              <div className="flex flex-col items-center gap-6 py-12">
                <div className="text-center">
                  <p className="text-4xl mb-2">🌾</p>
                  <p className="font-medium text-muted-foreground">
                    您好！我是农策助手
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    我能回答农业政策、补贴申请、土地流转等问题
                  </p>
                </div>
                {/* Quick questions */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
                  {QUICK_QUESTIONS.map((q) => (
                    <button
                      key={q}
                      onClick={() => handleSend(q)}
                      className="text-left text-sm rounded-lg border px-3 py-2 hover:bg-accent hover:border-primary transition-colors text-muted-foreground"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((msg, i) => (
              <MessageBubble
                key={msg.id}
                msg={msg}
                streaming={
                  isStreaming && i === messages.length - 1 && msg.role === "assistant"
                }
              />
            ))}
            <div ref={bottomRef} />
          </div>

          {/* Input area */}
          <div className="border-t px-4 py-3">
            <div className="flex gap-2 items-end">
              <Textarea
                ref={textareaRef}
                rows={2}
                className="resize-none flex-1"
                placeholder="输入政策问题，按 Enter 发送，Shift+Enter 换行…"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isStreaming}
              />
              <Button
                size="icon"
                className="h-10 w-10 shrink-0"
                onClick={() => handleSend()}
                disabled={isStreaming || !inputText.trim()}
              >
                {isStreaming ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
