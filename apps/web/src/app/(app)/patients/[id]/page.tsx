"use client";

import { use, useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import {
  Activity,
  Bot,
  ChevronLeft,
  ClipboardList,
  Heart,
  Pill,
  TestTube,
} from "lucide-react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "@/lib/api";
import { AnatomyCard } from "@/components/ui/AnatomyCard";
import { RiskBadge, news2ToRiskLevel, responseToRiskLevel } from "@/components/ui/RiskBadge";
import { SkeletonCard } from "@/components/ui/SkeletonTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { usePatientContext } from "@/contexts/PatientContext";

/* ── Types ── */
interface Comorbidity {
  htn: boolean; dm: boolean; insulin_dependent: boolean; ckd: boolean; copd: boolean;
  cad: boolean; prior_mi: boolean; afib: boolean; cvd_stroke: boolean; chf: boolean;
  smoking_current: boolean; smoking_former: boolean;
}
interface Lab {
  taken_at: string; creatinine: number | null; egfr: number | null; hb: number | null;
  platelets: number | null; inr: number | null; hba1c: number | null; bnp: number | null;
}
interface Medication { name: string; med_class: string; dose: string; }
interface Vital {
  taken_at: string; rr: number | null; spo2: number | null; on_oxygen: boolean;
  systolic_bp: number | null; heart_rate: number | null; temp_c: number | null; consciousness: string;
}
interface ClinicalNote { timestamp: string; note_type: string; author_role: string; body: string; }
interface PatientDetail {
  patient_id: string; name: string; age: number; dob: string | null; sex: string; mrn: string;
  aneurysm_type: string | null; location: string | null; max_diameter_mm: number | null;
  neck_length_mm: number | null; neck_angulation_deg: number | null; neck_diameter_mm: number | null;
  iliac_access_min_mm: number | null; iliac_access_max_mm: number | null;
  tortuosity: string | null; ct_scan_date: string | null;
  phase: string; planned_intervention: string; surgery_date: string | null;
  comorbidities: Comorbidity[]; labs: Lab[]; medications: Medication[];
  vitals: Vital[]; clinical_notes: ClinicalNote[];
}
interface Device {
  id: string; manufacturer: string; name: string; indication: string;
  ifu_proximal_min_mm: number; ifu_proximal_max_mm: number;
  ifu_distal_min_mm: number; ifu_distal_max_mm: number;
  ifu_min_neck_length_mm: number; ifu_max_neck_angulation_deg: number;
  ifu_iliac_min_mm: number; ifu_iliac_max_mm: number;
  ifu_length_options_mm: number[];
}
interface IFUCriterion { name: string; status: string; patient_value: number | string; ifu_threshold: string; note: string; }
interface IFUResult { device_name: string; overall: string; criteria: IFUCriterion[]; recommended_size_note: string; }
interface RiskResult { score?: number; risk_class?: string; estimated_risk_pct?: number; risk_category?: string; total_score?: number; response_level?: string; predicted_mortality_pct?: number; annual_stroke_risk_pct?: number; }

/* ── Tab definitions ── */
const TABS = ["overview", "risk", "notes", "postop", "ai"] as const;
type Tab = typeof TABS[number];
const TAB_LABELS: Record<Tab, string> = {
  overview: "Overview", risk: "Risk & Suitability", notes: "Notes", postop: "Post-op", ai: "AI Summary",
};

/* ── Comorbidity labels ── */
const COMORBIDITY_LABELS: Record<keyof Comorbidity, string> = {
  htn: "Hypertension", dm: "Diabetes mellitus", insulin_dependent: "Insulin-dependent DM",
  ckd: "Chronic kidney disease", copd: "COPD", cad: "Coronary artery disease",
  prior_mi: "Prior MI", afib: "Atrial fibrillation", cvd_stroke: "CVD / Prior stroke",
  chf: "Congestive heart failure", smoking_current: "Current smoker", smoking_former: "Former smoker",
};

const NOTE_TYPE_COLORS: Record<string, string> = {
  referral: "border-l-indigo-500", pre_op_assessment: "border-l-amber-500",
  op_note: "border-l-rose-500", progress: "border-l-emerald-500", discharge: "border-l-slate-500",
};

/* ── Overview Tab ── */
function OverviewTab({ patient }: { patient: PatientDetail }) {
  const comorbidity = patient.comorbidities[0];
  const latestLab = patient.labs.sort((a, b) => b.taken_at.localeCompare(a.taken_at))[0];

  return (
    <div className="space-y-4">
      <AnatomyCard
        aneurysmType={patient.aneurysm_type}
        location={patient.location}
        maxDiameterMm={patient.max_diameter_mm}
        neckLengthMm={patient.neck_length_mm}
        neckAngulationDeg={patient.neck_angulation_deg}
        neckDiameterMm={patient.neck_diameter_mm}
        iliacAccessMinMm={patient.iliac_access_min_mm}
        iliacAccessMaxMm={patient.iliac_access_max_mm}
        tortuosity={patient.tortuosity}
        ctScanDate={patient.ct_scan_date}
      />

      {/* Comorbidities */}
      <div className="rounded-lg border border-border bg-card p-4">
        <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
          <Heart className="h-4 w-4 text-rose-400" />
          Comorbidities
        </h3>
        {!comorbidity ? (
          <p className="text-xs text-muted-foreground">No comorbidity data recorded.</p>
        ) : (
          <ul className="grid grid-cols-2 sm:grid-cols-3 gap-1.5">
            {(Object.keys(COMORBIDITY_LABELS) as Array<keyof Comorbidity>).map((key) => (
              <li
                key={key}
                className={`flex items-center gap-2 text-xs py-1 px-2 rounded ${
                  comorbidity[key]
                    ? "bg-rose-900/20 text-rose-300"
                    : "text-muted-foreground"
                }`}
              >
                <span className={`h-2 w-2 rounded-full shrink-0 ${comorbidity[key] ? "bg-rose-400" : "bg-muted-foreground/30"}`} />
                {COMORBIDITY_LABELS[key]}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Latest labs */}
      <div className="rounded-lg border border-border bg-card p-4">
        <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
          <TestTube className="h-4 w-4 text-indigo-400" />
          Latest Labs {latestLab && <span className="text-xs text-muted-foreground font-normal">{new Date(latestLab.taken_at).toLocaleDateString()}</span>}
        </h3>
        {!latestLab ? (
          <p className="text-xs text-muted-foreground">No lab results recorded.</p>
        ) : (
          <dl className="grid grid-cols-3 sm:grid-cols-4 gap-3">
            {([
              ["Creatinine", latestLab.creatinine, "µmol/L"],
              ["eGFR", latestLab.egfr, "mL/min"],
              ["Hb", latestLab.hb, "g/dL"],
              ["Platelets", latestLab.platelets, "×10⁹/L"],
              ["INR", latestLab.inr, ""],
              ["HbA1c", latestLab.hba1c, "%"],
              ["BNP", latestLab.bnp, "pg/mL"],
            ] as [string, number | null, string][]).map(([label, val, unit]) => (
              <div key={label} className="flex flex-col gap-0.5">
                <dt className="text-xs text-muted-foreground">{label}</dt>
                <dd className="text-sm font-medium">
                  {val != null ? `${val}${unit ? ` ${unit}` : ""}` : <span className="text-muted-foreground italic">—</span>}
                </dd>
              </div>
            ))}
          </dl>
        )}
      </div>

      {/* Medications */}
      <div className="rounded-lg border border-border bg-card p-4">
        <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
          <Pill className="h-4 w-4 text-emerald-400" />
          Medications
        </h3>
        {patient.medications.length === 0 ? (
          <p className="text-xs text-muted-foreground">No medications recorded.</p>
        ) : (
          <ul className="space-y-1.5">
            {patient.medications.map((m, i) => (
              <li key={i} className="flex items-center justify-between text-sm">
                <span className="font-medium text-foreground">{m.name}</span>
                <span className="text-xs text-muted-foreground">{m.dose} — <span className="capitalize">{m.med_class.replace("_", " ")}</span></span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

/* ── Risk & Suitability Tab ── */
function RiskTab({ patient }: { patient: PatientDetail }) {
  const comorbidity = patient.comorbidities[0];
  const latestVital = patient.vitals.sort((a, b) => b.taken_at.localeCompare(a.taken_at))[0];
  const latestLab = patient.labs.sort((a, b) => b.taken_at.localeCompare(a.taken_at))[0];

  const { data: rcri } = useQuery({
    queryKey: ["rcri", patient.patient_id],
    enabled: !!comorbidity,
    queryFn: () =>
      api.post<RiskResult>("/risk/rcri", {
        high_risk_surgery: true,
        ischemic_heart_disease: comorbidity?.cad ?? false,
        congestive_heart_failure: comorbidity?.chf ?? false,
        cerebrovascular_disease: comorbidity?.cvd_stroke ?? false,
        insulin_dependent_diabetes: comorbidity?.insulin_dependent ?? false,
        preop_creatinine_gt_2: (latestLab?.creatinine ?? 0) > 177,
      }),
  });

  const { data: news2 } = useQuery({
    queryKey: ["news2", patient.patient_id],
    enabled: !!latestVital,
    queryFn: () =>
      api.post<RiskResult>("/risk/news2", {
        respiration_rate: latestVital?.rr ?? 16,
        spo2: latestVital?.spo2 ?? 98,
        on_supplemental_oxygen: latestVital?.on_oxygen ?? false,
        systolic_bp: latestVital?.systolic_bp ?? 120,
        heart_rate: latestVital?.heart_rate ?? 70,
        consciousness: latestVital?.consciousness ?? "A",
        temperature: latestVital?.temp_c ?? 36.5,
      }),
  });

  const { data: devices } = useQuery({
    queryKey: ["devices"],
    queryFn: () => api.get<Device[]>("/devices"),
  });

  const { data: ifuResults } = useQuery({
    queryKey: ["ifu-fit", patient.patient_id],
    enabled:
      !!devices &&
      patient.neck_length_mm != null &&
      patient.neck_angulation_deg != null &&
      patient.neck_diameter_mm != null &&
      patient.iliac_access_min_mm != null &&
      patient.max_diameter_mm != null,
    queryFn: () =>
      api.post<IFUResult[]>("/risk/ifu-fit", {
        neck_length_mm: patient.neck_length_mm,
        neck_angulation_deg: patient.neck_angulation_deg,
        neck_diameter_mm: patient.neck_diameter_mm,
        iliac_access_min_mm: patient.iliac_access_min_mm,
        max_diameter_mm: patient.max_diameter_mm,
        distal_landing_diameter_mm: null,
        devices: (devices ?? []).map((d) => ({
          name: d.name,
          ifu_min_neck_length_mm: d.ifu_min_neck_length_mm,
          ifu_max_neck_angulation_deg: d.ifu_max_neck_angulation_deg,
          ifu_proximal_min_mm: d.ifu_proximal_min_mm,
          ifu_proximal_max_mm: d.ifu_proximal_max_mm,
          ifu_iliac_min_mm: d.ifu_iliac_min_mm,
          ifu_iliac_max_mm: d.ifu_iliac_max_mm,
          ifu_distal_min_mm: d.ifu_distal_min_mm,
          ifu_distal_max_mm: d.ifu_distal_max_mm,
        })),
      }),
  });

  const ifuColor = (overall: string) => {
    if (overall === "suitable") return "text-emerald-400";
    if (overall === "borderline") return "text-amber-400";
    return "text-rose-400";
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* RCRI */}
        <div className="rounded-lg border border-border bg-card p-4">
          <h3 className="text-sm font-semibold mb-2">RCRI (Cardiac Risk)</h3>
          {!rcri ? (
            <SkeletonCard />
          ) : (
            <>
              <div className="text-3xl font-bold mb-1">{rcri.score ?? "—"}</div>
              <RiskBadge
                level={rcri.risk_class === "I" ? "low" : rcri.risk_class === "II" ? "medium" : rcri.risk_class === "III" ? "high" : "critical"}
                label={`Class ${rcri.risk_class} — ${rcri.estimated_risk_pct?.toFixed(1) ?? "?"}% 30-day MACE`}
              />
            </>
          )}
        </div>

        {/* NEWS2 */}
        <div className="rounded-lg border border-border bg-card p-4">
          <h3 className="text-sm font-semibold mb-2">NEWS2 (Acuity)</h3>
          {!news2 ? (
            <SkeletonCard />
          ) : (
            <>
              <div className="text-3xl font-bold mb-1">{news2.total_score ?? "—"}</div>
              {news2.total_score != null && (
                <RiskBadge
                  level={news2ToRiskLevel(news2.total_score)}
                  label={`${news2.response_level} response`}
                />
              )}
            </>
          )}
        </div>
      </div>

      {/* IFU-Fit Results */}
      <div className="rounded-lg border border-border bg-card">
        <div className="px-4 py-3 border-b border-border">
          <h3 className="text-sm font-semibold">Device IFU Suitability</h3>
          {(!patient.neck_length_mm || !patient.neck_angulation_deg || !patient.neck_diameter_mm || !patient.iliac_access_min_mm || !patient.max_diameter_mm) && (
            <p className="text-xs text-muted-foreground mt-0.5">Incomplete anatomy data — some IFU criteria cannot be evaluated.</p>
          )}
        </div>
        {!ifuResults ? (
          <div className="p-4 space-y-2">
            {[1, 2, 3].map((i) => <SkeletonCard key={i} />)}
          </div>
        ) : ifuResults.length === 0 ? (
          <EmptyState title="No devices available" className="border-0 rounded-t-none" />
        ) : (
          <div className="divide-y divide-border">
            {ifuResults.map((r) => (
              <details key={r.device_name} className="group">
                <summary className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-muted/20 transition-colors list-none">
                  <span className="text-sm font-medium text-foreground">{r.device_name}</span>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-semibold capitalize ${ifuColor(r.overall)}`}>{r.overall}</span>
                    <span className="text-muted-foreground text-xs group-open:rotate-90 transition-transform">▶</span>
                  </div>
                </summary>
                <div className="px-4 pb-3 space-y-1">
                  {r.criteria.map((c) => (
                    <div key={c.name} className="flex items-start justify-between text-xs gap-4">
                      <span className="text-muted-foreground">{c.name}</span>
                      <div className="text-right shrink-0">
                        <span className={c.status === "suitable" ? "text-emerald-400" : c.status === "borderline" ? "text-amber-400" : "text-rose-400"}>
                          {c.status}
                        </span>
                        <span className="text-muted-foreground ml-2">(pt: {c.patient_value} | IFU: {c.ifu_threshold})</span>
                      </div>
                    </div>
                  ))}
                  {r.recommended_size_note && (
                    <p className="text-xs text-muted-foreground mt-1 italic">{r.recommended_size_note}</p>
                  )}
                </div>
              </details>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Notes Tab ── */
function NotesTab({ notes }: { notes: ClinicalNote[] }) {
  const sorted = [...notes].sort((a, b) => b.timestamp.localeCompare(a.timestamp));
  if (sorted.length === 0) {
    return <EmptyState icon={ClipboardList} title="No clinical notes" />;
  }
  return (
    <div className="space-y-3">
      {sorted.map((n, i) => (
        <div
          key={i}
          className={`rounded-lg border border-border bg-card p-4 border-l-4 ${NOTE_TYPE_COLORS[n.note_type] ?? "border-l-muted"}`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-foreground capitalize">
              {n.note_type.replace(/_/g, " ")}
            </span>
            <div className="text-xs text-muted-foreground">
              {new Date(n.timestamp).toLocaleString()} · {n.author_role}
            </div>
          </div>
          <p className="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap">{n.body}</p>
        </div>
      ))}
    </div>
  );
}

/* ── Post-op Tab ── */
function PostOpTab({ vitals, patientId }: { vitals: Vital[]; patientId: string }) {
  const { data: latestNews2 } = useQuery({
    queryKey: ["news2-postop", patientId],
    enabled: vitals.length > 0,
    queryFn: () => {
      const v = [...vitals].sort((a, b) => b.taken_at.localeCompare(a.taken_at))[0];
      return api.post<RiskResult>("/risk/news2", {
        respiration_rate: v.rr ?? 16,
        spo2: v.spo2 ?? 98,
        on_supplemental_oxygen: v.on_oxygen,
        systolic_bp: v.systolic_bp ?? 120,
        heart_rate: v.heart_rate ?? 70,
        consciousness: v.consciousness ?? "A",
        temperature: v.temp_c ?? 36.5,
      });
    },
  });

  const sortedVitals = [...vitals]
    .sort((a, b) => a.taken_at.localeCompare(b.taken_at))
    .map((v) => ({
      time: new Date(v.taken_at).toLocaleDateString(),
      spo2: v.spo2,
      rr: v.rr,
      sbp: v.systolic_bp,
      hr: v.heart_rate,
      temp: v.temp_c,
    }));

  if (vitals.length === 0) {
    return <EmptyState icon={Activity} title="No vitals recorded" description="Vitals are available for post-operative patients." />;
  }

  return (
    <div className="space-y-4">
      {latestNews2 && (
        <div className="rounded-lg border border-border bg-card p-4 flex items-center gap-4">
          <div>
            <p className="text-xs text-muted-foreground">Latest NEWS2</p>
            <p className="text-3xl font-bold">{latestNews2.total_score}</p>
          </div>
          <RiskBadge
            level={responseToRiskLevel(latestNews2.response_level ?? "Low")}
            label={`${latestNews2.response_level} response`}
          />
        </div>
      )}

      {(["spo2", "sbp", "hr", "rr"] as const).map((key) => (
        <div key={key} className="rounded-lg border border-border bg-card p-4">
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
            {key === "spo2" ? "SpO₂ (%)" : key === "sbp" ? "Systolic BP (mmHg)" : key === "hr" ? "Heart Rate (bpm)" : "Resp. Rate (br/min)"}
          </h3>
          <ResponsiveContainer width="100%" height={120}>
            <LineChart data={sortedVitals} margin={{ top: 0, right: 0, bottom: 0, left: -25 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="time" tick={{ fontSize: 9, fill: "#94a3b8" }} />
              <YAxis tick={{ fontSize: 9, fill: "#94a3b8" }} />
              <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: 6, fontSize: 11 }} />
              <Line type="monotone" dataKey={key} stroke="#6366f1" dot={{ r: 2 }} strokeWidth={1.5} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ))}
    </div>
  );
}

/* ── AI Summary Tab ── */
function AISummaryTab({ patientId }: { patientId: string }) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["ai-summary", patientId],
    queryFn: () => api.post<{ patient_id: string; summary: string; sources: { id: string; type: string; title: string; body: string; source: string }[] }>(
      `/ai/patient-summary/${patientId}`, {}
    ),
    enabled: false,
    retry: false,
  });

  const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  if (!data && !isLoading && !error) {
    return (
      <div className="rounded-lg border border-border bg-card p-8 flex flex-col items-center gap-4 text-center">
        <Bot className="h-10 w-10 text-indigo-400" />
        <div>
          <p className="text-sm font-semibold text-foreground">AI Clinical Summary</p>
          <p className="text-xs text-muted-foreground mt-1 max-w-xs">
            Generate a Groq-powered, RAG-grounded clinical summary for this patient using guidelines from the knowledge base.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 rounded-md bg-indigo-700 hover:bg-indigo-600 text-white text-sm font-medium transition-colors"
        >
          Generate Summary
        </button>
        <p className="text-xs text-rose-400/80">
          ⚠️ Educational demo on synthetic data — not for clinical use; not medical advice.
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="rounded-lg border border-border bg-card p-8 flex flex-col items-center gap-3">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Bot className="h-5 w-5 animate-pulse text-indigo-400" />
          Generating AI summary via Groq…
        </div>
        <div className="w-full space-y-2 mt-2">
          {[1,2,3,4].map((i) => (
            <div key={i} className={`h-3 bg-muted/40 animate-pulse rounded ${i === 4 ? "w-2/3" : "w-full"}`} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    const msg = (error as Error).message;
    return (
      <div className="rounded-lg border border-border bg-card p-6 space-y-3">
        <p className="text-sm font-medium text-rose-400">Summary generation failed</p>
        <p className="text-xs text-muted-foreground">{msg.includes("GROQ") || msg.includes("503") ? "AI features require GROQ_API_KEY — add it to .env and restart the stack." : msg}</p>
        <button onClick={() => refetch()} className="text-xs text-indigo-400 hover:underline">Retry</button>
      </div>
    );
  }

  const token = typeof window !== "undefined" ? localStorage.getItem("pulse_access_token") : null;

  return (
    <div className="space-y-4">
      {/* Summary card */}
      <div className="rounded-lg border border-border bg-card p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="h-4 w-4 text-indigo-400" />
            <span className="text-sm font-semibold text-foreground">AI Clinical Summary</span>
          </div>
          <a
            href={`${API_URL}/ai/report/${patientId}${token ? `?token=${encodeURIComponent(token)}` : ""}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs px-3 py-1 rounded border border-indigo-700/50 text-indigo-400 hover:bg-indigo-900/30 transition-colors"
          >
            ↓ PDF Report
          </a>
        </div>
        <div className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
          {data?.summary}
        </div>
        <p className="text-xs text-rose-400/80 mt-2">
          ⚠️ Educational demo on synthetic data — not for clinical use; not medical advice.
        </p>
      </div>

      {/* Sources */}
      {data?.sources && data.sources.length > 0 && (
        <div className="rounded-lg border border-border bg-card divide-y divide-border">
          <div className="px-4 py-2">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
              Knowledge Base Sources ({data.sources.length})
            </p>
          </div>
          {data.sources.map((s, i) => (
            <details key={s.id} className="group">
              <summary className="flex items-center gap-2 px-4 py-2 cursor-pointer hover:bg-muted/20 list-none">
                <span className="text-xs font-mono text-muted-foreground shrink-0">[{i + 1}]</span>
                <span className="text-xs font-medium text-foreground flex-1">{s.title}</span>
                <span className="text-xs capitalize rounded-full px-1.5 py-0.5 bg-indigo-900/30 text-indigo-300">{s.type}</span>
              </summary>
              <div className="px-4 pb-3 pt-1 text-xs text-muted-foreground leading-relaxed">
                {s.body}
                <p className="mt-1 italic">{s.source}</p>
              </div>
            </details>
          ))}
        </div>
      )}

      <button
        onClick={() => refetch()}
        className="text-xs text-muted-foreground hover:text-foreground transition-colors"
      >
        Regenerate
      </button>
    </div>
  );
}

/* ── Main Page ── */
export default function PatientDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const { setPatient } = usePatientContext();
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  const { data: patient, isLoading, error } = useQuery({
    queryKey: ["patient", id],
    queryFn: () => api.get<PatientDetail>(`/patients/${id}`),
  });

  useEffect(() => {
    if (patient) setPatient(patient.patient_id, patient.name);
  }, [patient, setPatient]);

  if (isLoading) {
    return (
      <div className="px-6 py-6 space-y-4">
        <div className="h-6 w-48 bg-muted/50 animate-pulse rounded" />
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => <SkeletonCard key={i} />)}
        </div>
      </div>
    );
  }

  if (error || !patient) {
    return (
      <div className="px-6 py-6">
        <EmptyState title="Patient not found" description="This patient ID does not exist or you don't have access." />
      </div>
    );
  }

  const visibleTabs = TABS.filter((t) => t !== "postop" || patient.phase === "post");

  return (
    <div className="px-6 py-6 space-y-4">
      {/* Header */}
      <div>
        <button
          onClick={() => router.back()}
          className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors mb-3"
        >
          <ChevronLeft className="h-3 w-3" /> Back
        </button>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-foreground">{patient.name}</h1>
            <p className="text-sm text-muted-foreground">
              {patient.patient_id} · {patient.age}y {patient.sex} · MRN {patient.mrn}
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <span
              className={`text-xs font-medium capitalize px-2 py-1 rounded-full ${
                patient.phase === "post"
                  ? "bg-emerald-900/30 text-emerald-300"
                  : patient.phase === "intra"
                  ? "bg-amber-900/30 text-amber-300"
                  : "bg-indigo-900/30 text-indigo-300"
              }`}
            >
              {patient.phase}
            </span>
            <span className="text-xs text-muted-foreground border border-border rounded px-2 py-1">
              {patient.planned_intervention}
            </span>
          </div>
        </div>
        {patient.surgery_date && (
          <p className="text-xs text-muted-foreground mt-1">
            Surgery date: {new Date(patient.surgery_date).toLocaleDateString()}
          </p>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-border">
        <nav className="flex gap-0 -mb-px">
          {visibleTabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab
                  ? "border-indigo-500 text-foreground"
                  : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
              }`}
            >
              {TAB_LABELS[tab]}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      <div>
        {activeTab === "overview" && <OverviewTab patient={patient} />}
        {activeTab === "risk" && <RiskTab patient={patient} />}
        {activeTab === "notes" && <NotesTab notes={patient.clinical_notes} />}
        {activeTab === "postop" && patient.phase === "post" && (
          <PostOpTab vitals={patient.vitals} patientId={patient.patient_id} />
        )}
        {activeTab === "ai" && <AISummaryTab patientId={patient.patient_id} />}
      </div>
    </div>
  );
}
