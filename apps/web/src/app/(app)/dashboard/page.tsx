"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  AlertTriangle,
  Calendar,
  Users,
} from "lucide-react";
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "@/lib/api";
import { SkeletonCard, SkeletonTable } from "@/components/ui/SkeletonTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { RiskBadge } from "@/components/ui/RiskBadge";
import Link from "next/link";

interface DashboardStats {
  total_patients: number;
  by_phase: { pre: number; intra: number; post: number };
  high_news2_count: number;
  borderline_anatomy_count: number;
  challenging_anatomy_count: number;
  upcoming_procedures: number;
}

interface PatientListItem {
  patient_id: string;
  name: string;
  age: number;
  sex: string;
  aneurysm_type: string | null;
  max_diameter_mm: number | null;
  phase: string;
  planned_intervention: string;
}

const PHASE_COLORS: Record<string, string> = {
  pre: "#6366f1",
  intra: "#f59e0b",
  post: "#10b981",
};

const INTERVENTION_COLORS = ["#6366f1", "#8b5cf6", "#06b6d4", "#64748b"];

function KpiCard({
  label,
  value,
  sub,
  icon: Icon,
  accent,
}: {
  label: string;
  value: number | string;
  sub?: string;
  icon: React.ElementType;
  accent?: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-5">
      <div className="flex items-start justify-between mb-3">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</p>
        <div className={`rounded-md p-1.5 ${accent ?? "bg-indigo-900/40"}`}>
          <Icon className="h-4 w-4 text-indigo-300" />
        </div>
      </div>
      <p className="text-3xl font-bold text-foreground">{value}</p>
      {sub && <p className="mt-1 text-xs text-muted-foreground">{sub}</p>}
    </div>
  );
}

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: () => api.get<DashboardStats>("/dashboard/stats"),
  });

  const { data: patients, isLoading: patientsLoading } = useQuery({
    queryKey: ["patients-dashboard"],
    queryFn: () => api.get<PatientListItem[]>("/patients?limit=200&offset=0"),
  });

  const highRisk = patients
    ?.filter((p) => p.max_diameter_mm != null)
    .sort((a, b) => (b.max_diameter_mm ?? 0) - (a.max_diameter_mm ?? 0))
    .slice(0, 10) ?? [];

  const recent = patients?.slice(0, 6) ?? [];

  const phaseData = stats
    ? [
        { name: "Pre-op", value: stats.by_phase.pre, key: "pre" },
        { name: "Intra-op", value: stats.by_phase.intra, key: "intra" },
        { name: "Post-op", value: stats.by_phase.post, key: "post" },
      ]
    : [];

  const diameterBuckets: Record<string, number> = {};
  patients?.forEach((p) => {
    if (p.max_diameter_mm == null) return;
    const bucket = `${Math.floor(p.max_diameter_mm / 10) * 10}–${Math.floor(p.max_diameter_mm / 10) * 10 + 9}mm`;
    diameterBuckets[bucket] = (diameterBuckets[bucket] ?? 0) + 1;
  });
  const diameterData = Object.entries(diameterBuckets)
    .map(([range, count]) => ({ range, count }))
    .sort((a, b) => parseInt(a.range) - parseInt(b.range));

  const interventionCounts: Record<string, number> = {};
  patients?.forEach((p) => {
    interventionCounts[p.planned_intervention] = (interventionCounts[p.planned_intervention] ?? 0) + 1;
  });
  const interventionData = Object.entries(interventionCounts).map(([name, value]) => ({ name, value }));

  return (
    <div className="px-6 py-6 space-y-6">
      <div>
        <h1 className="text-xl font-bold text-foreground">Dashboard</h1>
        <p className="text-sm text-muted-foreground">Aortic surgery patient overview</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statsLoading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : (
          <>
            <KpiCard
              label="Total Patients"
              value={stats?.total_patients ?? 0}
              sub={`${stats?.by_phase.pre ?? 0} pre / ${stats?.by_phase.intra ?? 0} intra / ${stats?.by_phase.post ?? 0} post`}
              icon={Users}
            />
            <KpiCard
              label="High NEWS2 (≥7)"
              value={stats?.high_news2_count ?? 0}
              sub="Post-op patients needing urgent review"
              icon={Activity}
              accent="bg-rose-900/40"
            />
            <KpiCard
              label="Borderline Anatomy"
              value={stats?.borderline_anatomy_count ?? 0}
              sub="IFU-challenging morphology"
              icon={AlertTriangle}
              accent="bg-amber-900/40"
            />
            <KpiCard
              label="Upcoming (7 days)"
              value={stats?.upcoming_procedures ?? 0}
              sub="Scheduled interventions"
              icon={Calendar}
              accent="bg-emerald-900/40"
            />
          </>
        )}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Diameter histogram */}
        <div className="lg:col-span-2 rounded-lg border border-border bg-card p-4">
          <h2 className="text-sm font-semibold text-foreground mb-4">Aneurysm Size Distribution</h2>
          {patientsLoading ? (
            <div className="h-48 animate-pulse bg-muted/30 rounded" />
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={diameterData} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                <XAxis dataKey="range" tick={{ fontSize: 10, fill: "#94a3b8" }} />
                <YAxis tick={{ fontSize: 10, fill: "#94a3b8" }} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: 6 }}
                  labelStyle={{ color: "#e2e8f0", fontSize: 11 }}
                  itemStyle={{ color: "#94a3b8", fontSize: 11 }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Phase bar + intervention donut */}
        <div className="space-y-4">
          <div className="rounded-lg border border-border bg-card p-4">
            <h2 className="text-sm font-semibold text-foreground mb-3">Phase Distribution</h2>
            {statsLoading ? (
              <div className="h-28 animate-pulse bg-muted/30 rounded" />
            ) : (
              <ResponsiveContainer width="100%" height={100}>
                <BarChart data={phaseData} layout="vertical" margin={{ top: 0, right: 0, bottom: 0, left: 10 }}>
                  <XAxis type="number" tick={{ fontSize: 10, fill: "#94a3b8" }} hide />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: "#94a3b8" }} width={50} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: 6 }}
                    itemStyle={{ color: "#94a3b8", fontSize: 11 }}
                  />
                  <Bar dataKey="value" radius={[0, 3, 3, 0]}>
                    {phaseData.map((entry) => (
                      <Cell key={entry.key} fill={PHASE_COLORS[entry.key] ?? "#6366f1"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="rounded-lg border border-border bg-card p-4">
            <h2 className="text-sm font-semibold text-foreground mb-1">Intervention Mix</h2>
            {patientsLoading ? (
              <div className="h-24 animate-pulse bg-muted/30 rounded" />
            ) : (
              <ResponsiveContainer width="100%" height={90}>
                <PieChart>
                  <Pie
                    data={interventionData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={25}
                    outerRadius={40}
                  >
                    {interventionData.map((_, i) => (
                      <Cell key={i} fill={INTERVENTION_COLORS[i % INTERVENTION_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: 6 }}
                    itemStyle={{ color: "#94a3b8", fontSize: 11 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* High-risk shortlist */}
      <div className="rounded-lg border border-border bg-card">
        <div className="px-4 py-3 border-b border-border flex items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground">High-Risk Shortlist (by diameter)</h2>
          <Link href="/patients" className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">
            View all →
          </Link>
        </div>
        {patientsLoading ? (
          <SkeletonTable rows={5} cols={5} className="rounded-t-none border-0" />
        ) : highRisk.length === 0 ? (
          <EmptyState title="No patients with anatomy data" className="border-0 rounded-t-none" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-xs text-muted-foreground">
                  <th className="text-left px-4 py-2">ID</th>
                  <th className="text-left px-4 py-2">Name</th>
                  <th className="text-left px-4 py-2">Age/Sex</th>
                  <th className="text-left px-4 py-2">Type</th>
                  <th className="text-right px-4 py-2">Diameter</th>
                  <th className="text-left px-4 py-2">Phase</th>
                  <th className="text-left px-4 py-2">Intervention</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {highRisk.map((p) => (
                  <tr
                    key={p.patient_id}
                    className="hover:bg-muted/20 transition-colors"
                  >
                    <td className="px-4 py-2 font-mono text-xs text-muted-foreground">
                      <Link href={`/patients/${p.patient_id}`} className="hover:text-indigo-400 transition-colors">
                        {p.patient_id}
                      </Link>
                    </td>
                    <td className="px-4 py-2 font-medium">{p.name}</td>
                    <td className="px-4 py-2 text-muted-foreground">{p.age}y {p.sex}</td>
                    <td className="px-4 py-2 text-muted-foreground">{p.aneurysm_type ?? "—"}</td>
                    <td className="px-4 py-2 text-right">
                      {p.max_diameter_mm != null ? (
                        <RiskBadge
                          level={p.max_diameter_mm >= 70 ? "critical" : p.max_diameter_mm >= 55 ? "high" : "medium"}
                          label={`${p.max_diameter_mm} mm`}
                        />
                      ) : "—"}
                    </td>
                    <td className="px-4 py-2">
                      <span className="text-xs capitalize text-muted-foreground">{p.phase}</span>
                    </td>
                    <td className="px-4 py-2 text-xs text-muted-foreground">{p.planned_intervention}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recent patients */}
      <div>
        <h2 className="text-sm font-semibold text-foreground mb-3">Recent Patients</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {patientsLoading
            ? Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="rounded-lg border border-border bg-card p-3 animate-pulse">
                  <div className="h-3 bg-muted/50 rounded mb-2" />
                  <div className="h-4 bg-muted/50 rounded mb-1" />
                  <div className="h-3 bg-muted/50 rounded w-2/3" />
                </div>
              ))
            : recent.map((p) => (
                <Link
                  key={p.patient_id}
                  href={`/patients/${p.patient_id}`}
                  className="rounded-lg border border-border bg-card p-3 hover:border-indigo-700/50 hover:bg-indigo-900/10 transition-colors block"
                >
                  <p className="text-xs text-muted-foreground font-mono mb-1">{p.patient_id}</p>
                  <p className="text-sm font-medium text-foreground truncate">{p.name}</p>
                  <p className="text-xs text-muted-foreground mt-0.5 capitalize">{p.phase} • {p.planned_intervention}</p>
                </Link>
              ))}
        </div>
      </div>
    </div>
  );
}
