"use client";

import { useCurrentUser } from "@/hooks/useCurrentUser";

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

function DisabledToggle({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-2 opacity-40 cursor-not-allowed" title="Available in v0.3 after adding a Groq key">
      <span className="text-xs text-muted-foreground">{label}</span>
      <div className="h-5 w-9 rounded-full bg-muted border border-border" />
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
            <span className="text-xs capitalize rounded-full bg-indigo-900/40 text-indigo-300 border border-indigo-700/30 px-2 py-0.5">
              {user?.role ?? "—"}
            </span>
          </SettingRow>
        </div>
      </section>

      {/* Appearance */}
      <section>
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">Appearance</h2>
        <div className="rounded-lg border border-border bg-card px-4">
          <SettingRow label="Theme" description="Interface colour scheme">
            <div className="flex items-center gap-2">
              <span className="text-xs rounded-full bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5">
                Dark (default)
              </span>
            </div>
          </SettingRow>
        </div>
      </section>

      {/* AI — Phase 2 */}
      <section>
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">
          AI Copilot
          <span className="ml-2 text-xs font-normal normal-case text-indigo-400">— unlocks in v0.3 after adding a Groq key</span>
        </h2>
        <div className="rounded-lg border border-border bg-card px-4">
          <SettingRow
            label="Default model"
            description="Groq model used for patient summaries and journey generation"
          >
            <DisabledToggle label="llama-3.3-70b" />
          </SettingRow>
          <SettingRow
            label="Rerank results"
            description="Use a cross-encoder to rerank RAG retrieval results before answering"
          >
            <DisabledToggle label="Off" />
          </SettingRow>
          <SettingRow
            label="Streaming responses"
            description="Stream the AI copilot token-by-token"
          >
            <DisabledToggle label="On" />
          </SettingRow>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          To enable: add <code className="font-mono bg-muted/30 px-1 rounded">GROQ_API_KEY=gsk_...</code> to{" "}
          <code className="font-mono bg-muted/30 px-1 rounded">.env</code> and restart the stack.
        </p>
      </section>

      {/* About */}
      <section>
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">About</h2>
        <div className="rounded-lg border border-border bg-card px-4">
          <SettingRow label="Version" description="Pulse release">
            <span className="text-xs text-muted-foreground font-mono">v0.2.0</span>
          </SettingRow>
          <SettingRow label="Data" description="All patient data is synthetic — generated for demonstration only">
            <span className="text-xs rounded-full bg-amber-900/30 text-amber-300 border border-amber-700/30 px-2 py-0.5">
              Synthetic
            </span>
          </SettingRow>
        </div>
      </section>
    </div>
  );
}
