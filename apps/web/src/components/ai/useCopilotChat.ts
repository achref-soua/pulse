"use client";

import { useCallback, useRef, useState } from "react";

export interface Source {
  id?: string;
  type?: string;
  title: string;
  source?: string;
  body?: string;
}

export interface AgentStep {
  id: string;
  kind: "router" | "tool";
  label: string;
  status: "running" | "done";
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  steps: AgentStep[];
  sources: Source[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// Friendly labels for the tool chips in the agent timeline.
const TOOL_LABELS: Record<string, string> = {
  calculate_risk_score: "Calculating risk score",
  get_patient: "Reading patient record",
  match_devices: "Matching devices to anatomy",
  search_guidelines: "Searching guidelines",
  search_device_catalog: "Searching device catalog",
  get_device: "Looking up device IFU",
  query_cohort: "Querying the cohort",
  search_patient_notes: "Searching clinical notes",
};

function toolLabel(name: string): string {
  return TOOL_LABELS[name] ?? name.replace(/_/g, " ");
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("pulse_access_token");
}

const GREETING: ChatMessage = {
  role: "assistant",
  content:
    "I'm the Pulse clinical agent. Ask me to score a patient, match a stent-graft, or search the guidelines — I call the deterministic clinical engine for every number and cite what I use.\n\n⚠️ Educational demo on synthetic data — not for clinical use; not medical advice.",
  steps: [],
  sources: [],
};

/** Shared SSE-consuming chat state for the copilot panel and the /copilot page. */
export function useCopilotChat(patientId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING]);
  const [streaming, setStreaming] = useState(false);
  const threadRef = useRef<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Mutate the assistant message currently being built (always the last one).
  const patchLast = useCallback((fn: (m: ChatMessage) => ChatMessage) => {
    setMessages((prev) => {
      const copy = [...prev];
      copy[copy.length - 1] = fn(copy[copy.length - 1]);
      return copy;
    });
  }, []);

  const send = useCallback(
    async (text: string) => {
      const message = text.trim();
      if (!message || streaming) return;
      setMessages((prev) => [
        ...prev,
        { role: "user", content: message, steps: [], sources: [] },
        { role: "assistant", content: "", steps: [], sources: [] },
      ]);
      setStreaming(true);

      const ctrl = new AbortController();
      abortRef.current = ctrl;
      const token = getToken();

      try {
        const res = await fetch(`${API_URL}/ai/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            message,
            patient_id: patientId ?? undefined,
            thread_id: threadRef.current ?? undefined,
          }),
          signal: ctrl.signal,
        });
        if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

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
              handleEvent(JSON.parse(line.slice(6)), patchLast, threadRef);
            } catch {
              /* malformed SSE line — skip */
            }
          }
        }
      } catch (err: unknown) {
        if (err instanceof Error && err.name !== "AbortError") {
          patchLast((m) => ({
            ...m,
            content:
              "Sorry — the AI service is unavailable. Check that GROQ_API_KEY is set and the stack is running.",
          }));
        }
      } finally {
        // Any tool still marked running when the stream ends is complete.
        patchLast((m) => ({
          ...m,
          steps: m.steps.map((s) => ({ ...s, status: "done" as const })),
        }));
        setStreaming(false);
      }
    },
    [patientId, streaming, patchLast],
  );

  const stop = useCallback(() => abortRef.current?.abort(), []);
  const reset = useCallback(() => {
    threadRef.current = null;
    setMessages([GREETING]);
  }, []);

  return { messages, streaming, send, stop, reset };
}

export interface SSEvent {
  type: string;
  name?: string;
  content?: unknown;
}

/** Pure reducer: fold one SSE event into the assistant message being built. */
export function reduceMessage(m: ChatMessage, evt: SSEvent): ChatMessage {
  switch (evt.type) {
    case "router":
      return {
        ...m,
        steps: [
          ...m.steps,
          {
            id: `router-${m.steps.length}`,
            kind: "router",
            label: evt.content === "direct" ? "Answering directly" : "Planning with tools",
            status: "done",
          },
        ],
      };
    case "tool_call":
      return {
        ...m,
        steps: [
          ...m.steps,
          {
            id: `tool-${evt.name}-${m.steps.length}`,
            kind: "tool",
            label: toolLabel(evt.name ?? ""),
            status: "running",
          },
        ],
      };
    case "tool_result": {
      const steps = [...m.steps];
      for (let i = steps.length - 1; i >= 0; i--) {
        if (steps[i].kind === "tool" && steps[i].label === toolLabel(evt.name ?? "")) {
          steps[i] = { ...steps[i], status: "done" };
          break;
        }
      }
      return { ...m, steps };
    }
    case "sources":
      return Array.isArray(evt.content)
        ? { ...m, sources: dedupeSources([...m.sources, ...(evt.content as Source[])]) }
        : m;
    case "token":
      return { ...m, content: m.content + String(evt.content) };
    case "error":
      // Backend signalled a failure mid-stream (e.g. AI provider error/rate limit).
      // Surface it instead of leaving an empty bubble.
      return {
        ...m,
        content:
          m.content ||
          String(evt.content ?? "") ||
          "The AI service hit an error — please try again in a moment.",
      };
    default:
      return m;
  }
}

function handleEvent(
  evt: SSEvent,
  patchLast: (fn: (m: ChatMessage) => ChatMessage) => void,
  threadRef: React.MutableRefObject<string | null>,
) {
  if (evt.type === "thread") {
    threadRef.current = String(evt.content);
    return;
  }
  patchLast((m) => reduceMessage(m, evt));
}

function dedupeSources(sources: Source[]): Source[] {
  const seen = new Set<string>();
  return sources.filter((s) => {
    const key = s.title ?? s.id ?? "";
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}
