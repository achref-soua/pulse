"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Bot, Loader2, Maximize2, RotateCcw, Send, X } from "lucide-react";
import { cn } from "@pulse/ui";
import { usePatientContext } from "@/contexts/PatientContext";
import { useCopilotChat } from "./useCopilotChat";
import { MessageBubble } from "./AgentTrace";
import { SuggestedPrompts } from "./SuggestedPrompts";

export function AICopilotPanel({ onClose }: { onClose: () => void }) {
  const { patientId, patientName } = usePatientContext();
  const { messages, streaming, send, reset } = useCopilotChat(patientId);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function submit() {
    const text = input.trim();
    if (!text || streaming) return;
    setInput("");
    void send(text);
  }

  return (
    <div className="fixed bottom-20 right-4 z-50 flex max-h-[640px] w-[420px] flex-col rounded-xl border border-border bg-card shadow-2xl">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center rounded-md bg-primary/10">
            <Bot className="h-4 w-4 text-primary" />
          </span>
          <span className="text-sm font-semibold text-foreground">Clinical Agent</span>
          {patientName && <span className="text-xs text-muted-foreground">· {patientName}</span>}
        </div>
        <div className="flex items-center gap-1 text-muted-foreground">
          <button onClick={reset} title="New conversation" className="rounded p-1 hover:text-foreground">
            <RotateCcw className="h-3.5 w-3.5" />
          </button>
          <Link href="/copilot" title="Open full copilot" className="rounded p-1 hover:text-foreground">
            <Maximize2 className="h-3.5 w-3.5" />
          </Link>
          <button onClick={onClose} title="Close" className="rounded p-1 hover:text-foreground">
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-4 py-3">
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} streaming={streaming && i === messages.length - 1} />
        ))}
        {messages.length === 1 && !streaming && (
          <SuggestedPrompts hasPatient={!!patientId} onPick={(p) => void send(p)} />
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex items-end gap-2 border-t border-border px-3 py-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Ask to score, match a device, or search guidelines…"
          rows={2}
          disabled={streaming}
          className="flex-1 resize-none rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
        />
        <button
          onClick={submit}
          disabled={!input.trim() || streaming}
          className={cn(
            "flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-40",
          )}
        >
          {streaming ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </button>
      </div>
    </div>
  );
}
