"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { X } from "lucide-react";
import { usePatientContext } from "@/contexts/PatientContext";

const routeLabels: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/patients": "Patients",
  "/risk": "Risk Tools",
  "/devices": "Devices",
  "/monitoring": "Monitoring",
  "/admin": "Admin",
  "/settings": "Settings",
};

function getBreadcrumb(pathname: string): { label: string; href: string }[] {
  const parts = pathname.split("/").filter(Boolean);
  const crumbs: { label: string; href: string }[] = [];

  if (parts[0]) {
    const base = `/${parts[0]}`;
    crumbs.push({ label: routeLabels[base] ?? parts[0], href: base });
  }
  if (parts[1]) {
    crumbs.push({ label: parts[1], href: `/${parts[0]}/${parts[1]}` });
  }
  if (parts[2]) {
    crumbs.push({ label: parts[2], href: pathname });
  }

  return crumbs;
}

export function TopBar() {
  const pathname = usePathname();
  const { patientId, patientName, clearPatient } = usePatientContext();
  const crumbs = getBreadcrumb(pathname);

  return (
    <header className="fixed top-0 left-60 right-0 z-30 flex h-12 items-center border-b border-border bg-card/80 backdrop-blur-sm px-4 gap-4">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1.5 text-sm min-w-0 flex-1">
        {crumbs.map((c, i) => (
          <span key={c.href} className="flex items-center gap-1.5 min-w-0">
            {i > 0 && <span className="text-muted-foreground">/</span>}
            <Link
              href={c.href}
              className={
                i === crumbs.length - 1
                  ? "font-medium text-foreground truncate"
                  : "text-muted-foreground hover:text-foreground transition-colors truncate"
              }
            >
              {c.label}
            </Link>
          </span>
        ))}
      </nav>

      {/* Patient-in-context chip */}
      {patientId && patientName && (
        <div className="flex items-center gap-1.5 rounded-full bg-indigo-900/40 border border-indigo-700/40 px-3 py-1 shrink-0">
          <span className="text-xs text-indigo-300 font-medium">
            {patientId} — {patientName}
          </span>
          <button
            onClick={clearPatient}
            className="text-indigo-400 hover:text-indigo-200 transition-colors"
            title="Clear patient context"
          >
            <X className="h-3 w-3" />
          </button>
        </div>
      )}
    </header>
  );
}
