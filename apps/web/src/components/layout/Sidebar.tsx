"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Activity,
  BarChart2,
  BookOpen,
  ChevronRight,
  Cpu,
  LayoutDashboard,
  LogOut,
  Settings,
  ShieldCheck,
  Users,
} from "lucide-react";
import { cn } from "@pulse/ui";

const PulseLogo = () => (
  <svg width="110" height="28" viewBox="0 0 220 56" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="Pulse">
    <polyline
      points="0,28 10,28 15,28 19,12 23,44 27,8 31,40 35,28 45,28"
      stroke="#e11d48"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <line x1="57" y1="8" x2="57" y2="48" stroke="#c7d2fe" strokeWidth="1.5" />
    <text
      x="67"
      y="40"
      fontFamily="'Inter','Helvetica Neue',Arial,sans-serif"
      fontSize="32"
      fontWeight="800"
      letterSpacing="-1"
      fill="#3730a3"
    >
      PULSE
    </text>
  </svg>
);

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/patients", label: "Patients", icon: Users },
  { href: "/risk", label: "Risk Tools", icon: ShieldCheck },
  { href: "/devices", label: "Devices", icon: Cpu },
  { href: "/monitoring", label: "Monitoring", icon: Activity },
  { href: "/knowledge", label: "Knowledge Base", icon: BookOpen },
];

const adminItems = [
  { href: "/admin", label: "Admin", icon: BarChart2 },
  { href: "/settings", label: "Settings", icon: Settings },
];

interface NavItemProps {
  href: string;
  label: string;
  icon: React.ElementType;
  active: boolean;
}

function NavItem({ href, label, icon: Icon, active }: NavItemProps) {
  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
        active
          ? "bg-indigo-900/60 text-indigo-200"
          : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
      )}
    >
      <Icon className="h-4 w-4 shrink-0" />
      <span>{label}</span>
      {active && <ChevronRight className="ml-auto h-3 w-3 opacity-50" />}
    </Link>
  );
}

interface SidebarProps {
  userRole: string;
  userEmail: string;
  userFullName: string;
}

export function Sidebar({ userRole, userEmail, userFullName }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    localStorage.removeItem("pulse_access_token");
    localStorage.removeItem("pulse_refresh_token");
    router.push("/login");
  }

  return (
    <aside className="fixed inset-y-0 left-0 z-40 flex w-60 flex-col border-r border-border bg-card">
      {/* Logo */}
      <div className="flex items-center px-4 py-4 border-b border-border">
        <PulseLogo />
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-1">
        {navItems.map((item) => (
          <NavItem
            key={item.href}
            {...item}
            active={pathname === item.href || pathname.startsWith(item.href + "/")}
          />
        ))}
        <div className="my-2 border-t border-border" />
        {adminItems.map((item) => (
          <NavItem
            key={item.href}
            {...item}
            active={pathname === item.href}
          />
        ))}
      </nav>

      {/* User chip */}
      <div className="border-t border-border px-3 py-3">
        <div className="flex items-center gap-2 mb-2">
          <div className="h-7 w-7 rounded-full bg-indigo-800 flex items-center justify-center text-xs font-semibold text-indigo-200 shrink-0">
            {userFullName?.charAt(0).toUpperCase() ?? "?"}
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium text-foreground truncate">{userFullName}</p>
            <p className="text-xs text-muted-foreground truncate">{userEmail}</p>
          </div>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs rounded-full bg-indigo-900/50 text-indigo-300 px-2 py-0.5 border border-indigo-700/30 capitalize">
            {userRole}
          </span>
          <button
            onClick={handleLogout}
            className="text-muted-foreground hover:text-foreground transition-colors"
            title="Sign out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
