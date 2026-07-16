"use client";

import { useCurrentUser } from "@/hooks/useCurrentUser";
import { ThemeToggle } from "@/components/ui/ThemeToggle";

function SettingRow({ label, description, children }: { label: string; description?: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-4 border-b border-border last:border-0">
      <div>
        <p className="text-sm font-medium text-foreground">{label}</p>
        {description && <p className="text-xs text-muted-foreground mt-0.5">{description}</p>}
      </div>
      {children}
    </div>
  );
}


export default function SettingsPage() {
  const user = useCurrentUser();

  return (
    <div className="px-6 py-6 max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-bold text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground">Account and workspace configuration</p>
      </div>

      {/* Account */}
      <section>
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">Account</h2>
        <div className="rounded-lg border border-border bg-card px-4">
          <SettingRow label="Name" description="Display name for this account">
            <span className="text-sm text-muted-foreground">{user?.fullName ?? "—"}</span>
          </SettingRow>
          <SettingRow label="Email">
            <span className="text-sm text-muted-foreground">{user?.email ?? "—"}</span>
          </SettingRow>
          <SettingRow label="Role" description="Assigned by an admin">
            <span className="rounded-full border border-primary/25 bg-primary/10 px-2 py-0.5 text-xs capitalize text-primary">
              {user?.role ?? "—"}
            </span>
          </SettingRow>
        </div>
      </section>

      {/* Appearance */}
      <section>
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">Appearance</h2>
        <div className="rounded-lg border border-border bg-card px-4">
          <SettingRow label="Theme" description="Light, dark, or match your system">
            <ThemeToggle />
          </SettingRow>
        </div>
      </section>

      {/* AI Copilot */}
      <section>
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">
          AI Copilot
          <span className="ml-2 text-xs font-normal normal-case text-success">— active (GROQ_API_KEY set)</span>
        </h2>
        <div className="rounded-lg border border-border bg-card px-4">
          <SettingRow
            label="Default model"
            description="Groq model used for patient summaries and streaming chat"
          >
            <span className="rounded border border-primary/25 bg-primary/10 px-2 py-0.5 font-mono text-xs text-primary">
              llama-3.3-70b-versatile
            </span>
          </SettingRow>
          <SettingRow
            label="Reranking"
            description="Cross-encoder (ms-marco-MiniLM-L-6-v2) reranks RAG candidates before generation"
          >
            <span className="rounded-full border border-success/25 bg-success/10 px-2 py-0.5 text-xs text-success">
              Enabled
            </span>
          </SettingRow>
          <SettingRow
            label="Streaming"
            description="Chat responses stream token-by-token via SSE"
          >
            <span className="rounded-full border border-success/25 bg-success/10 px-2 py-0.5 text-xs text-success">
              Enabled
            </span>
          </SettingRow>
          <SettingRow
            label="Knowledge base"
            description="Guidelines and literature indexed in Quiver (vector search)"
          >
            <span className="text-xs text-muted-foreground">13 entries</span>
          </SettingRow>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          Model and rerank settings are configured via env vars:{" "}
          <code className="font-mono bg-muted/30 px-1 rounded">GROQ_MODEL</code>,{" "}
          <code className="font-mono bg-muted/30 px-1 rounded">RERANK_ENABLED</code>.
        </p>
      </section>

      {/* About */}
      <section>
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">About</h2>
        <div className="rounded-lg border border-border bg-card px-4">
          <SettingRow label="Version" description="Pulse release">
            <span className="text-xs text-muted-foreground font-mono">v1.0.0</span>
          </SettingRow>
          <SettingRow label="Data" description="All patient data is synthetic — generated for demonstration only">
            <span className="rounded-full border border-warning/25 bg-warning/10 px-2 py-0.5 text-xs text-warning">
              Synthetic
            </span>
          </SettingRow>
        </div>
      </section>
    </div>
  );
}
