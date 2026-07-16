"use client";

import { Sparkles } from "lucide-react";

const WITH_PATIENT = [
  "What's this patient's RCRI and NEWS2?",
  "Is this patient suitable for EVAR? Match the devices.",
  "Summarise the pre-op risk picture with guideline support.",
];

const GENERAL = [
  "How many pre-op EVAR patients are in the cohort?",
  "What are the IFU neck-length requirements for EVAR?",
  "What is a Type Ia endoleak?",
];

export function SuggestedPrompts({
  hasPatient,
  onPick,
}: {
  hasPatient: boolean;
  onPick: (prompt: string) => void;
}) {
  const prompts = hasPatient ? WITH_PATIENT : GENERAL;
  return (
    <div className="space-y-1.5">
      <p className="flex items-center gap-1 px-1 text-xs font-medium text-muted-foreground">
        <Sparkles className="h-3 w-3 text-primary" /> Try asking
      </p>
      {prompts.map((p) => (
        <button
          key={p}
          onClick={() => onPick(p)}
          className="block w-full rounded-md border border-border bg-card px-3 py-2 text-left text-xs text-foreground transition-colors hover:border-primary/40 hover:bg-primary/5"
        >
          {p}
        </button>
      ))}
    </div>
  );
}
