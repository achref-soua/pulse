"use client";

import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { ShieldAlert } from "lucide-react";
import { api } from "@/lib/api";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { SkeletonTable } from "@/components/ui/SkeletonTable";
import { EmptyState } from "@/components/ui/EmptyState";

interface UserItem { id: string; email: string; full_name: string; role: string; is_active: boolean; }
interface AuditEntry { id: string; user_id: string | null; action: string; entity: string; entity_id: string | null; ip_address: string | null; created_at: string; }

const ROLES = ["surgeon", "anesthetist", "nurse", "admin"] as const;

export default function AdminPage() {
  const router = useRouter();
  const user = useCurrentUser();
  const qc = useQueryClient();
  const [tab, setTab] = useState<"users" | "audit">("users");

  useEffect(() => {
    if (user && user.role !== "admin") router.replace("/dashboard");
  }, [user, router]);

  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ["users"],
    enabled: user?.role === "admin",
    queryFn: () => api.get<UserItem[]>("/users"),
  });

  const { data: auditLog, isLoading: auditLoading } = useQuery({
    queryKey: ["audit-log"],
    enabled: tab === "audit" && user?.role === "admin",
    queryFn: () => api.get<AuditEntry[]>("/users/audit-log?limit=100"),
  });

  const roleMutation = useMutation({
    mutationFn: ({ id, role }: { id: string; role: string }) =>
      api.patch(`/users/${id}/role`, { role }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["users"] }),
  });

  const activeMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      api.patch(`/users/${id}/active`, { is_active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["users"] }),
  });

  if (!user || user.role !== "admin") {
    return (
      <div className="px-6 py-6">
        <EmptyState icon={ShieldAlert} title="Admin only" description="This page is restricted to admin users." />
      </div>
    );
  }

  return (
    <div className="px-6 py-6 space-y-4">
      <div>
        <h1 className="text-xl font-bold text-foreground">Admin</h1>
        <p className="text-sm text-muted-foreground">User management and audit log</p>
      </div>

      <div className="border-b border-border">
        <nav className="flex gap-0 -mb-px">
          {(["users", "audit"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors capitalize ${
                tab === t
                  ? "border-indigo-500 text-foreground"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              {t === "users" ? "Users" : "Audit Log"}
            </button>
          ))}
        </nav>
      </div>

      {tab === "users" && (
        usersLoading ? (
          <SkeletonTable rows={5} cols={4} />
        ) : !users || users.length === 0 ? (
          <EmptyState title="No users found" />
        ) : (
          <div className="rounded-lg border border-border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted/20 border-b border-border text-xs text-muted-foreground">
                <tr>
                  <th className="text-left px-4 py-3">Name</th>
                  <th className="text-left px-4 py-3">Email</th>
                  <th className="text-left px-4 py-3">Role</th>
                  <th className="text-left px-4 py-3">Active</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-muted/10 transition-colors">
                    <td className="px-4 py-3 font-medium">{u.full_name}</td>
                    <td className="px-4 py-3 text-muted-foreground text-xs">{u.email}</td>
                    <td className="px-4 py-3">
                      <select
                        value={u.role}
                        onChange={(e) => roleMutation.mutate({ id: u.id, role: e.target.value })}
                        className="text-xs rounded border border-border bg-card px-2 py-1 focus:outline-none focus:ring-1 focus:ring-indigo-700 text-foreground"
                      >
                        {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() =>
                          activeMutation.mutate({ id: u.id, is_active: !u.is_active })
                        }
                        disabled={u.id === user.id}
                        className={`text-xs px-2 py-1 rounded-full border transition-colors disabled:opacity-40 ${
                          u.is_active
                            ? "bg-emerald-900/30 text-emerald-300 border-emerald-700/40 hover:bg-emerald-900/50"
                            : "bg-muted/30 text-muted-foreground border-border hover:bg-muted/50"
                        }`}
                      >
                        {u.is_active ? "Active" : "Inactive"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      {tab === "audit" && (
        auditLoading ? (
          <SkeletonTable rows={8} cols={5} />
        ) : !auditLog || auditLog.length === 0 ? (
          <EmptyState title="No audit entries" />
        ) : (
          <div className="rounded-lg border border-border overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted/20 border-b border-border text-xs text-muted-foreground">
                  <tr>
                    <th className="text-left px-4 py-3">Time</th>
                    <th className="text-left px-4 py-3">Action</th>
                    <th className="text-left px-4 py-3">Entity</th>
                    <th className="text-left px-4 py-3">Entity ID</th>
                    <th className="text-left px-4 py-3">IP</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {auditLog.map((e) => (
                    <tr key={e.id} className="hover:bg-muted/10 transition-colors">
                      <td className="px-4 py-2 text-xs text-muted-foreground whitespace-nowrap">
                        {new Date(e.created_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-2 text-xs font-medium">{e.action}</td>
                      <td className="px-4 py-2 text-xs text-muted-foreground">{e.entity}</td>
                      <td className="px-4 py-2 font-mono text-xs text-muted-foreground truncate max-w-[120px]">{e.entity_id ?? "—"}</td>
                      <td className="px-4 py-2 text-xs text-muted-foreground">{e.ip_address ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )
      )}
    </div>
  );
}
