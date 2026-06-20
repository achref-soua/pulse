"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Bot } from "lucide-react";
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
        <main className="pt-12 pb-10 min-h-screen">{children}</main>
      </div>

      {/* Floating AI Copilot */}
      <button
        onClick={() => setCopilotOpen((o) => !o)}
        title="AI Copilot"
        className={`fixed bottom-4 right-4 z-40 flex items-center gap-2 rounded-full px-4 py-2.5 text-sm font-medium shadow-lg transition-colors ${
          copilotOpen
            ? "bg-indigo-600 text-white"
            : "bg-indigo-700 hover:bg-indigo-600 text-white"
        }`}
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
