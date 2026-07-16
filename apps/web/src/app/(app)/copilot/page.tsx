"use client";

import { useEffect, useRef, useState } from "react";
import { Bot, Loader2, RotateCcw, Send } from "lucide-react";
import { usePatientContext } from "@/contexts/PatientContext";
import { useCopilotChat } from "@/components/ai/useCopilotChat";
import { MessageBubble } from "@/components/ai/AgentTrace";
import { SuggestedPrompts } from "@/components/ai/SuggestedPrompts";

export default function CopilotPage() {
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
    <div className="mx-auto flex h-[calc(100vh-3.5rem)] max-w-3xl flex-col px-4 py-6">
      <div className="mb-4 flex items-start justify-between">
        <div className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
            <Bot className="h-5 w-5 text-primary" />
          </span>
          <div>
            <h1 className="text-lg font-bold text-foreground">Clinical Agent</h1>
            <p className="text-xs text-muted-foreground">
              Tool-calling agent · deterministic scoring · grounded citations
              {patientName && ` · ${patientName}`}
            </p>
          </div>
        </div>
        <button
          onClick={reset}
          className="flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
        >
          <RotateCcw className="h-3.5 w-3.5" /> New chat
        </button>
      </div>

      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto rounded-lg border border-border bg-card px-4 py-4">
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} streaming={streaming && i === messages.length - 1} />
        ))}
        {messages.length === 1 && !streaming && (
          <div className="mx-auto max-w-md pt-4">
            <SuggestedPrompts hasPatient={!!patientId} onPick={(p) => void send(p)} />
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="mt-3 flex items-end gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Ask to score a patient, match a stent-graft, or search the guidelines…"
          rows={2}
          disabled={streaming}
          className="flex-1 resize-none rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
        />
        <button
          onClick={submit}
          disabled={!input.trim() || streaming}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-40"
        >
          {streaming ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </button>
      </div>
      <p className="mt-2 text-center text-[11px] text-muted-foreground">
        ⚠️ Educational demo on synthetic data — not for clinical use; not medical advice.
      </p>
    </div>
  );
}
