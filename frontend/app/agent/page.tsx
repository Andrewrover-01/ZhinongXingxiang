"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2, Bot, Wrench } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Nav } from "@/components/nav";
import { cn } from "@/lib/utils";

interface AgentMessage {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string;
  toolName?: string;
  timestamp: Date;
}

const SUGGESTIONS = [
  "帮我制定下周的灌溉计划",
  "当前季节需要施什么肥？",
  "如何防治水稻纹枯病？",
  "本月有哪些重要农事节点？",
];

function AgentMessageBubble({ msg }: { msg: AgentMessage }) {
  if (msg.role === "tool") {
    return (
      <div className="flex items-start gap-2 text-xs text-muted-foreground">
        <Wrench className="h-3.5 w-3.5 mt-0.5 shrink-0" />
        <div className="bg-muted rounded-lg px-3 py-1.5 flex-1">
          <span className="font-medium text-foreground/70">
            工具调用: {msg.toolName}
          </span>
          <pre className="whitespace-pre-wrap mt-0.5 opacity-80">{msg.content}</pre>
        </div>
      </div>
    );
  }

  const isUser = msg.role === "user";
  return (
    <div className={cn("flex gap-2", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0 mt-0.5">
          <Bot className="h-4 w-4 text-primary" />
        </div>
      )}
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
          isUser
            ? "bg-primary text-primary-foreground rounded-tr-sm"
            : "bg-muted text-foreground rounded-tl-sm"
        )}
      >
        <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
      </div>
      {isUser && (
        <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center text-sm shrink-0 mt-0.5">
          👤
        </div>
      )}
    </div>
  );
}

export default function AgentPage() {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend(text?: string) {
    const msgText = (text ?? inputText).trim();
    if (!msgText || isThinking) return;
    setInputText("");

    const userMsg: AgentMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      content: msgText,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsThinking(true);

    // Simulate agent thinking with tool calls (backend not yet implemented)
    await new Promise((r) => setTimeout(r, 800));

    // Simulated tool call
    const toolMsg: AgentMessage = {
      id: `t-${Date.now()}`,
      role: "tool",
      toolName: "get_farm_context",
      content: "查询农田信息和当前季节气象数据…",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, toolMsg]);

    await new Promise((r) => setTimeout(r, 600));

    // Simulated assistant response
    const assistantMsg: AgentMessage = {
      id: `a-${Date.now()}`,
      role: "assistant",
      content:
        "🤖 农事 Agent 功能正在建设中（第四阶段）。\n\n" +
        "当前已支持：\n" +
        "• 🩺 AI 医生病虫害诊断\n" +
        "• 📋 农策助手政策问答\n" +
        "• 📊 农情数据看板\n\n" +
        "敬请期待更多 Agent 能力！",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, assistantMsg]);
    setIsThinking(false);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Nav />
      <div className="flex-1 flex flex-col max-w-2xl mx-auto w-full">
        {/* Header */}
        <div className="border-b px-4 py-3 flex items-center gap-3">
          <Bot className="h-5 w-5 text-primary" />
          <h1 className="font-semibold">🤖 农事 Agent</h1>
          <Badge variant="secondary" className="ml-auto text-xs">
            Beta
          </Badge>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center gap-6 py-12">
              <div className="text-center">
                <p className="text-5xl mb-3">🤖</p>
                <p className="font-medium">农事 Agent</p>
                <p className="text-sm text-muted-foreground mt-1">
                  智能农事规划，自动调用工具为您服务
                </p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full">
                {SUGGESTIONS.map((q) => (
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

          {messages.map((msg) => (
            <AgentMessageBubble key={msg.id} msg={msg} />
          ))}

          {isThinking && (
            <div className="flex items-center gap-2 text-muted-foreground text-sm">
              <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                <Bot className="h-4 w-4 text-primary" />
              </div>
              <div className="bg-muted rounded-2xl px-4 py-2.5 flex items-center gap-2">
                <Loader2 className="h-3 w-3 animate-spin" />
                <span>思考中…</span>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t px-4 py-3">
          <div className="flex gap-2 items-end">
            <Textarea
              rows={2}
              className="resize-none flex-1"
              placeholder="告诉我您的农事需求，Enter 发送…"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isThinking}
            />
            <Button
              size="icon"
              className="h-10 w-10 shrink-0"
              onClick={() => handleSend()}
              disabled={isThinking || !inputText.trim()}
            >
              {isThinking ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
