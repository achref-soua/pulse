"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Bot } from "lucide-react";
import { cn } from "@pulse/ui";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { AICopilotPanel } from "@/components/ai/AICopilotPanel";
import { PatientContextProvider } from "@/contexts/PatientContext";
import { useCurrentUser } from "@/hooks/useCurrentUser";

function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const user = useCurrentUser();
  const [copilotOpen, setCopilotOpen] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("pulse_access_token");
    if (!token) {
      router.replace("/login");
    }
  }, [router]);

  if (!user) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar
        userRole={user.role}
        userEmail={user.email}
        userFullName={user.fullName}
      />
      <div className="flex-1 ml-60">
        <TopBar />
        <main className="min-h-screen pb-10 pt-14">{children}</main>
      </div>

      {/* Floating AI Copilot */}
      <button
        onClick={() => setCopilotOpen((o) => !o)}
        title="AI Copilot"
        className={cn(
          "fixed bottom-4 right-4 z-40 flex items-center gap-2 rounded-full bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground shadow-lg transition-all hover:shadow-glow active:translate-y-px",
          copilotOpen && "shadow-glow"
        )}
      >
        <Bot className="h-4 w-4" />
        AI Copilot
      </button>

      {copilotOpen && <AICopilotPanel onClose={() => setCopilotOpen(false)} />}
    </div>
  );
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <PatientContextProvider>
      <AppShell>{children}</AppShell>
    </PatientContextProvider>
  );
}
