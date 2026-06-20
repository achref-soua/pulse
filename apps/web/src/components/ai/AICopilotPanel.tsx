"use client";

import { useEffect, useRef, useState } from "react";
import { Bot, Send, X, Loader2, BookOpen } from "lucide-react";
import { usePatientContext } from "@/contexts/PatientContext";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

interface Source {
  id: string;
  type: string;
  title: string;
  score?: number | null;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("pulse_access_token");
}

export function AICopilotPanel({ onClose }: { onClose: () => void }) {
  const { patientId, patientName } = usePatientContext();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello — I'm the Pulse AI Copilot. I can answer questions about aortic and endovascular surgery guidelines, help interpret anatomy, and summarise patient context.\n\n⚠️ Educational demo on synthetic data — not for clinical use; not medical advice.",
    },
  ]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text || streaming) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setStreaming(true);

    const token = getToken();
    const ctrl = new AbortController();
    abortRef.current = ctrl;

    // Placeholder for the assistant reply being built
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "", sources: [] },
    ]);

    try {
      const res = await fetch(`${API_URL}/ai/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ message: text, patient_id: patientId ?? undefined }),
        signal: ctrl.signal,
      });

      if (!res.ok || !res.body) {
        throw new Error(`HTTP ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split("\n");
        buf = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const evt = JSON.parse(line.slice(6));
            if (evt.type === "sources") {
              setMessages((prev) => {
                const copy = [...prev];
                copy[copy.length - 1] = {
                  ...copy[copy.length - 1],
                  sources: evt.content,
                };
                return copy;
              });
            } else if (evt.type === "token") {
              setMessages((prev) => {
                const copy = [...prev];
                copy[copy.length - 1] = {
                  ...copy[copy.length - 1],
                  content: (copy[copy.length - 1].content ?? "") + evt.content,
                };
                return copy;
              });
            }
          } catch {
            // malformed SSE line — skip
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== "AbortError") {
        setMessages((prev) => {
          const copy = [...prev];
          copy[copy.length - 1] = {
            ...copy[copy.length - 1],
            content: "Sorry, the AI service is unavailable. Check that GROQ_API_KEY is set and the stack is running.",
          };
          return copy;
        });
      }
    } finally {
      setStreaming(false);
    }
  }

  return (
    <div className="fixed bottom-20 right-4 z-50 w-[420px] max-h-[600px] flex flex-col rounded-xl border border-border bg-card shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-indigo-400" />
          <span className="text-sm font-semibold text-foreground">AI Copilot</span>
          {patientName && (
            <span className="text-xs text-muted-foreground">· {patientName}</span>
          )}
        </div>
        <button
          onClick={onClose}
          className="text-muted-foreground hover:text-foreground transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 min-h-0">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[88%] rounded-lg px-3 py-2 text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-indigo-700/60 text-white"
                  : "bg-muted/30 text-foreground"
              }`}
            >
              {m.content || (streaming && i === messages.length - 1 ? (
                <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />
              ) : "")}
              {m.sources && m.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-border/50 space-y-0.5">
                  {m.sources.slice(0, 3).map((s) => (
                    <div key={s.id} className="flex items-start gap-1">
                      <BookOpen className="h-2.5 w-2.5 mt-0.5 shrink-0 text-indigo-400" />
                      <span className="text-xs text-muted-foreground leading-snug">{s.title}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-border px-3 py-2 flex items-end gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
          placeholder="Ask about guidelines, anatomy, risk…"
          rows={2}
          disabled={streaming}
          className="flex-1 resize-none rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-700 disabled:opacity-50 placeholder:text-muted-foreground"
        />
        <button
          onClick={send}
          disabled={!input.trim() || streaming}
          className="shrink-0 flex items-center justify-center h-9 w-9 rounded-md bg-indigo-700 hover:bg-indigo-600 text-white transition-colors disabled:opacity-40"
        >
          {streaming ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </button>
      </div>
    </div>
  );
}
