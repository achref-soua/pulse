"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { PatientContextProvider } from "@/contexts/PatientContext";
import { useCurrentUser } from "@/hooks/useCurrentUser";

function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const user = useCurrentUser();

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
