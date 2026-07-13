"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useState, Suspense } from "react";
import { Loader2, Search, Sparkles, Users, X } from "lucide-react";
import { api } from "@/lib/api";
import { RiskBadge, RiskLevel } from "@/components/ui/RiskBadge";
import { SkeletonTable } from "@/components/ui/SkeletonTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { usePatientContext } from "@/contexts/PatientContext";

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

const PHASES = ["", "pre", "intra", "post"];
const INTERVENTIONS = ["", "EVAR", "TEVAR", "open_graft", "surveillance"];
const PAGE_SIZE = 50;

function diameterRisk(mm: number | null): RiskLevel {
  if (mm == null) return "low";
  if (mm >= 70) return "critical";
  if (mm >= 55) return "high";
  if (mm >= 45) return "medium";
  return "low";
}

function PatientsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setPatient } = usePatientContext();

  const search = searchParams.get("search") ?? "";
  const phase = searchParams.get("phase") ?? "";
  const intervention = searchParams.get("intervention") ?? "";
  const offset = parseInt(searchParams.get("offset") ?? "0", 10);
  // Extra filters the NL→cohort feature can set (no dedicated controls in the UI).
  const nlKeys = ["aneurysm_type", "sex", "min_diameter_mm", "min_age", "max_age"] as const;
  const nlActive = nlKeys.some((k) => searchParams.get(k));

  const [nlQuery, setNlQuery] = useState("");

  function setParam(key: string, value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value) params.set(key, value);
    else params.delete(key);
    if (key !== "offset") params.delete("offset");
    router.push(`/patients?${params.toString()}`);
  }

  function applyFilters(filters: Record<string, unknown>) {
    const params = new URLSearchParams();
    for (const [k, v] of Object.entries(filters)) {
      if (v !== null && v !== undefined && v !== "") params.set(k, String(v));
    }
    router.push(`/patients?${params.toString()}`);
  }

  function clearNl() {
    const params = new URLSearchParams(searchParams.toString());
    nlKeys.forEach((k) => params.delete(k));
    router.push(`/patients?${params.toString()}`);
  }

  const nlMutation = useMutation({
    mutationFn: (query: string) =>
      api.post<{ filters: Record<string, unknown> }>("/ai/nl-cohort", { query }),
    onSuccess: (res) => applyFilters(res.filters),
  });

  const queryString = [
    `limit=${PAGE_SIZE}`,
    `offset=${offset}`,
    search && `search=${encodeURIComponent(search)}`,
    phase && `phase=${phase}`,
    intervention && `intervention=${intervention}`,
    ...nlKeys.map((k) => {
      const v = searchParams.get(k);
      return v && `${k}=${encodeURIComponent(v)}`;
    }),
  ]
    .filter(Boolean)
    .join("&");

  const { data: patients, isLoading } = useQuery({
    queryKey: ["patients", queryString],
    queryFn: () => api.get<PatientListItem[]>(`/patients?${queryString}`),
  });

  const handleRowClick = useCallback(
    (p: PatientListItem) => {
      setPatient(p.patient_id, p.name);
      router.push(`/patients/${p.patient_id}`);
    },
    [router, setPatient]
  );

  return (
    <div className="px-6 py-6 space-y-4">
      <div>
        <h1 className="text-xl font-bold text-foreground">Patients</h1>
        <p className="text-sm text-muted-foreground">
          {patients ? `${patients.length} results` : "Loading…"}
        </p>
      </div>

      {/* Natural-language cohort search */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (nlQuery.trim()) nlMutation.mutate(nlQuery.trim());
        }}
        className="relative"
      >
        <Sparkles className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-primary" />
        <input
          type="text"
          value={nlQuery}
          onChange={(e) => setNlQuery(e.target.value)}
          placeholder="Ask in plain English — e.g. “post-op patients with large aneurysms over 75”"
          className="w-full rounded-lg border border-border bg-card py-2.5 pl-9 pr-24 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <button
          type="submit"
          disabled={!nlQuery.trim() || nlMutation.isPending}
          className="absolute right-1.5 top-1/2 flex -translate-y-1/2 items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground disabled:opacity-40"
        >
          {nlMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Search"}
        </button>
      </form>
      {nlActive && (
        <button
          onClick={clearNl}
          className="inline-flex items-center gap-1.5 rounded-full border border-primary/25 bg-primary/10 px-3 py-1 text-xs text-primary"
        >
          AI filter active <X className="h-3 w-3" />
        </button>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search name or ID…"
            value={search}
            onChange={(e) => setParam("search", e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-sm rounded-md border border-border bg-card focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <select
          value={phase}
          onChange={(e) => setParam("phase", e.target.value)}
          className="text-sm rounded-md border border-border bg-card px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary text-foreground"
        >
          {PHASES.map((p) => (
            <option key={p} value={p}>
              {p ? `Phase: ${p}` : "All phases"}
            </option>
          ))}
        </select>
        <select
          value={intervention}
          onChange={(e) => setParam("intervention", e.target.value)}
          className="text-sm rounded-md border border-border bg-card px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary text-foreground"
        >
          {INTERVENTIONS.map((i) => (
            <option key={i} value={i}>
              {i ? `Intervention: ${i}` : "All interventions"}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      {isLoading ? (
        <SkeletonTable rows={8} cols={7} />
      ) : !patients || patients.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No patients found"
          description="Try adjusting your search or filters."
        />
      ) : (
        <div className="rounded-lg border border-border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/20 border-b border-border">
                <tr className="text-xs text-muted-foreground">
                  <th className="text-left px-4 py-3">ID</th>
                  <th className="text-left px-4 py-3">Name</th>
                  <th className="text-left px-4 py-3">Age / Sex</th>
                  <th className="text-left px-4 py-3">Type</th>
                  <th className="text-right px-4 py-3">Diameter</th>
                  <th className="text-left px-4 py-3">Phase</th>
                  <th className="text-left px-4 py-3">Intervention</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {patients.map((p) => (
                  <tr
                    key={p.patient_id}
                    onClick={() => handleRowClick(p)}
                    className="hover:bg-muted/20 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                      {p.patient_id}
                    </td>
                    <td className="px-4 py-3 font-medium text-foreground">{p.name}</td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {p.age}y {p.sex}
                    </td>
                    <td className="px-4 py-3 text-muted-foreground text-xs">
                      {p.aneurysm_type ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {p.max_diameter_mm != null ? (
                        <RiskBadge
                          level={diameterRisk(p.max_diameter_mm)}
                          label={`${p.max_diameter_mm} mm`}
                        />
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`text-xs font-medium capitalize ${
                          p.phase === "post"
                            ? "text-success"
                            : p.phase === "intra"
                            ? "text-warning"
                            : "text-primary"
                        }`}
                      >
                        {p.phase}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">
                      {p.planned_intervention}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="px-4 py-3 border-t border-border flex items-center justify-between">
            <span className="text-xs text-muted-foreground">
              Showing {offset + 1}–{offset + (patients?.length ?? 0)}
            </span>
            <div className="flex gap-2">
              <button
                disabled={offset === 0}
                onClick={() => setParam("offset", String(Math.max(0, offset - PAGE_SIZE)))}
                className="text-xs px-3 py-1 rounded border border-border bg-card hover:bg-muted/30 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                ← Previous
              </button>
              <button
                disabled={(patients?.length ?? 0) < PAGE_SIZE}
                onClick={() => setParam("offset", String(offset + PAGE_SIZE))}
                className="text-xs px-3 py-1 rounded border border-border bg-card hover:bg-muted/30 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Next →
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function PatientsPage() {
  return (
    <Suspense fallback={<div className="px-6 py-6"><SkeletonTable rows={8} cols={7} /></div>}>
      <PatientsContent />
    </Suspense>
  );
}
