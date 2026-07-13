"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import { useTheme } from "next-themes";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  BarChart2,
  BookOpen,
  Bot,
  Cpu,
  LayoutDashboard,
  Moon,
  Search,
  ShieldCheck,
  Sun,
  User,
  Users,
} from "lucide-react";
import { api } from "@/lib/api";

interface PatientHit {
  patient_id: string;
  name: string;
  age: number;
  aneurysm_type: string | null;
}
interface DeviceHit {
  id: string;
  manufacturer: string;
  name: string;
  indication: string;
}

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/patients", label: "Patients", icon: Users },
  { href: "/copilot", label: "Copilot", icon: Bot },
  { href: "/risk", label: "Risk Tools", icon: ShieldCheck },
  { href: "/devices", label: "Devices", icon: Cpu },
  { href: "/monitoring", label: "Monitoring", icon: Activity },
  { href: "/knowledge", label: "Knowledge Base", icon: BookOpen },
  { href: "/admin", label: "Admin", icon: BarChart2 },
];

export function CommandPalette() {
  const router = useRouter();
  const { theme, setTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  // Global ⌘K / Ctrl+K toggle.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((o) => !o);
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  // Let the TopBar button open the palette without prop-drilling.
  useEffect(() => {
    const openIt = () => setOpen(true);
    window.addEventListener("pulse:open-command", openIt);
    return () => window.removeEventListener("pulse:open-command", openIt);
  }, []);

  // Live patient search (only while open and with a query).
  const { data: patients } = useQuery({
    queryKey: ["cmd-patients", query],
    queryFn: () => api.get<PatientHit[]>(`/patients?search=${encodeURIComponent(query)}&limit=6`),
    enabled: open && query.trim().length > 0,
  });
  // Device catalog is small — load once when the palette opens.
  const { data: devices } = useQuery({
    queryKey: ["cmd-devices"],
    queryFn: () => api.get<DeviceHit[]>("/devices"),
    enabled: open,
    staleTime: 5 * 60 * 1000,
  });

  function run(action: () => void) {
    setOpen(false);
    setQuery("");
    action();
  }

  return (
    <Command.Dialog
      open={open}
      onOpenChange={setOpen}
      label="Command palette"
      shouldFilter={false}
      className="fixed left-1/2 top-[20%] z-[60] w-[92vw] max-w-lg -translate-x-1/2 overflow-hidden rounded-xl border border-border bg-popover shadow-2xl"
    >
      <div className="flex items-center gap-2 border-b border-border px-3">
        <Search className="h-4 w-4 text-muted-foreground" />
        <Command.Input
          value={query}
          onValueChange={setQuery}
          placeholder="Search patients, devices, actions…"
          className="flex-1 bg-transparent py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
        />
      </div>
      <Command.List className="max-h-[360px] overflow-y-auto p-2">
        <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
          No results.
        </Command.Empty>

        {(patients ?? []).length > 0 && (
          <Command.Group heading="Patients" className="text-xs text-muted-foreground [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5">
            {patients!.map((p) => (
              <Item key={p.patient_id} onSelect={() => run(() => router.push(`/patients/${p.patient_id}`))}>
                <User className="h-4 w-4 text-primary" />
                <span className="text-foreground">{p.name}</span>
                <span className="ml-auto text-xs text-muted-foreground">
                  {p.patient_id} · {p.age}y {p.aneurysm_type ?? ""}
                </span>
              </Item>
            ))}
          </Command.Group>
        )}

        <Command.Group heading="Navigate" className="text-xs text-muted-foreground [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5">
          {NAV.map((n) => (
            <Item key={n.href} onSelect={() => run(() => router.push(n.href))}>
              <n.icon className="h-4 w-4 text-muted-foreground" />
              <span className="text-foreground">{n.label}</span>
            </Item>
          ))}
        </Command.Group>

        {(devices ?? []).length > 0 && (
          <Command.Group heading="Devices" className="text-xs text-muted-foreground [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5">
            {devices!
              .filter((d) =>
                query.trim()
                  ? `${d.manufacturer} ${d.name}`.toLowerCase().includes(query.toLowerCase())
                  : true,
              )
              .slice(0, 6)
              .map((d) => (
                <Item key={d.id} onSelect={() => run(() => router.push("/devices"))}>
                  <Cpu className="h-4 w-4 text-muted-foreground" />
                  <span className="text-foreground">
                    {d.manufacturer} {d.name}
                  </span>
                  <span className="ml-auto text-xs text-muted-foreground">{d.indication}</span>
                </Item>
              ))}
          </Command.Group>
        )}

        <Command.Group heading="Actions" className="text-xs text-muted-foreground [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5">
          <Item onSelect={() => run(() => setTheme(theme === "dark" ? "light" : "dark"))}>
            {theme === "dark" ? <Sun className="h-4 w-4 text-muted-foreground" /> : <Moon className="h-4 w-4 text-muted-foreground" />}
            <span className="text-foreground">Toggle {theme === "dark" ? "light" : "dark"} mode</span>
          </Item>
          <Item onSelect={() => run(() => router.push("/copilot"))}>
            <Bot className="h-4 w-4 text-muted-foreground" />
            <span className="text-foreground">Ask the clinical agent</span>
          </Item>
        </Command.Group>
      </Command.List>
    </Command.Dialog>
  );
}

function Item({ children, onSelect }: { children: React.ReactNode; onSelect: () => void }) {
  return (
    <Command.Item
      onSelect={onSelect}
      className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-2 text-sm data-[selected=true]:bg-primary/10 data-[selected=true]:text-foreground"
    >
      {children}
    </Command.Item>
  );
}
