"use client";

import { BookOpen, Check, Loader2, Route, Wrench } from "lucide-react";
import { cn } from "@pulse/ui";
import type { AgentStep, ChatMessage, Source } from "./useCopilotChat";
import { Markdown } from "./Markdown";

function StepChip({ step }: { step: AgentStep }) {
  const Icon = step.status === "running" ? Loader2 : step.kind === "router" ? Route : Wrench;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs",
        step.status === "running"
          ? "border-primary/40 bg-primary/10 text-primary"
          : "border-border bg-muted/60 text-muted-foreground",
      )}
    >
      <Icon className={cn("h-3 w-3", step.status === "running" && "animate-spin")} />
      {step.label}
      {step.status === "done" && step.kind === "tool" && <Check className="h-3 w-3 text-success" />}
    </span>
  );
}

export function AgentTimeline({ steps }: { steps: AgentStep[] }) {
  if (!steps.length) return null;
  return (
    <div className="mb-2 flex flex-wrap gap-1.5">
      {steps.map((s) => (
        <StepChip key={s.id} step={s} />
      ))}
    </div>
  );
}

export function SourceCards({ sources }: { sources: Source[] }) {
  if (!sources.length) return null;
  return (
    <div className="mt-2 space-y-1.5 border-t border-border/50 pt-2">
      <p className="text-xs font-medium text-muted-foreground">Grounded in</p>
      {sources.slice(0, 5).map((s, i) => (
        <div key={s.id ?? i} className="flex items-start gap-1.5 rounded-md bg-muted/40 px-2 py-1.5">
          <BookOpen className="mt-0.5 h-3 w-3 shrink-0 text-primary" />
          <div className="min-w-0">
            <p className="truncate text-xs font-medium text-foreground">{s.title}</p>
            {s.source && <p className="truncate text-[11px] text-muted-foreground">{s.source}</p>}
          </div>
        </div>
      ))}
    </div>
  );
}

/** One chat bubble — user or assistant with its agent timeline, markdown, and sources. */
export function MessageBubble({ message, streaming }: { message: ChatMessage; streaming: boolean }) {
  const isUser = message.role === "user";
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[88%] rounded-lg px-3 py-2 text-sm",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted/50 text-foreground",
        )}
      >
        {!isUser && <AgentTimeline steps={message.steps} />}
        {message.content ? (
          isUser ? (
            <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
          ) : (
            <Markdown content={message.content} />
          )
        ) : streaming ? (
          <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />
        ) : null}
        {!isUser && <SourceCards sources={message.sources} />}
      </div>
    </div>
  );
}
