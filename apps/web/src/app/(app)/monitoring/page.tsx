"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity } from "lucide-react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "@/lib/api";
import { RiskBadge, news2ToRiskLevel } from "@/components/ui/RiskBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { SkeletonTable } from "@/components/ui/SkeletonTable";

interface Vital {
  taken_at: string; rr: number | null; spo2: number | null; on_oxygen: boolean;
  systolic_bp: number | null; heart_rate: number | null; temp_c: number | null; consciousness: string;
}
interface Patient {
  patient_id: string; name: string; age: number; sex: string;
  aneurysm_type: string | null; max_diameter_mm: number | null;
  phase: string; planned_intervention: string;
}
interface PatientDetail extends Patient {
  comorbidities: unknown[]; labs: unknown[]; medications: unknown[];
  vitals: Vital[]; clinical_notes: unknown[];
}
function news2Score(v: Vital): number {
  const rr = v.rr ?? 16;
  const spo2 = v.spo2 ?? 98;
  const sbp = v.systolic_bp ?? 120;
  const hr = v.heart_rate ?? 70;
  const temp = v.temp_c ?? 36.5;
  const rrS = rr <= 8 ? 3 : rr <= 11 ? 1 : rr <= 20 ? 0 : rr <= 24 ? 2 : 3;
  const spo2S = spo2 <= 91 ? 3 : spo2 <= 93 ? 2 : spo2 <= 94 ? 1 : v.on_oxygen ? 2 : 0;
  const sbpS = sbp <= 90 ? 3 : sbp <= 100 ? 2 : sbp <= 110 ? 1 : sbp <= 219 ? 0 : 3;
  const hrS = hr <= 40 ? 3 : hr <= 50 ? 1 : hr <= 90 ? 0 : hr <= 110 ? 1 : hr <= 130 ? 2 : 3;
  const tempS = temp <= 35 ? 3 : temp <= 36 ? 1 : temp <= 38 ? 0 : temp <= 39 ? 1 : 2;
  const avpu = v.consciousness === "A" ? 0 : 3;
  return rrS + spo2S + sbpS + hrS + tempS + avpu;
}

function PatientVitalsCard({ detail }: { detail: PatientDetail }) {
  const sorted = [...detail.vitals].sort((a, b) => a.taken_at.localeCompare(b.taken_at));
  const latest = sorted.at(-1);
  const score = latest ? news2Score(latest) : 0;
  const level = news2ToRiskLevel(score);

  const chartData = sorted.slice(-10).map((v) => ({
    time: new Date(v.taken_at).toLocaleDateString(),
    spo2: v.spo2,
    sbp: v.systolic_bp,
    hr: v.heart_rate,
  }));

  return (
    <div className="rounded-lg border border-border bg-card">
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-foreground">{detail.name}</p>
          <p className="text-xs text-muted-foreground">{detail.patient_id} · {detail.age}y {detail.sex}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-2xl font-bold text-foreground">{score}</span>
          <RiskBadge level={level} label={level === "critical" ? "High" : level === "high" ? "Medium" : "Low"} />
        </div>
      </div>
      {chartData.length > 1 && (
        <div className="px-4 py-3">
          <ResponsiveContainer width="100%" height={80}>
            <LineChart data={chartData} margin={{ top: 0, right: 0, bottom: 0, left: -30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" tick={{ fontSize: 8, fill: "#64748b" }} />
              <YAxis tick={{ fontSize: 8, fill: "#64748b" }} />
              <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", fontSize: 10 }} />
              <Line type="monotone" dataKey="spo2" stroke="#6366f1" dot={false} strokeWidth={1.5} name="SpO₂" />
              <Line type="monotone" dataKey="sbp" stroke="#f59e0b" dot={false} strokeWidth={1.5} name="SBP" />
              <Line type="monotone" dataKey="hr" stroke="#10b981" dot={false} strokeWidth={1.5} name="HR" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export default function MonitoringPage() {
  const { data: postPatients, isLoading } = useQuery({
    queryKey: ["patients-post"],
    queryFn: () => api.get<Patient[]>("/patients?phase=post&limit=200"),
  });

  const patientIds = postPatients?.map((p) => p.patient_id) ?? [];

  const detailQueries = useQuery({
    queryKey: ["patients-post-details", patientIds.join(",")],
    enabled: patientIds.length > 0,
    queryFn: async () => {
      const details = await Promise.all(
        patientIds.slice(0, 20).map((id) => api.get<PatientDetail>(`/patients/${id}`))
      );
      return details;
    },
  });

  const withScores = (detailQueries.data ?? [])
    .map((d) => {
      const latest = [...d.vitals].sort((a, b) => b.taken_at.localeCompare(a.taken_at))[0];
      return { detail: d, score: latest ? news2Score(latest) : 0 };
    })
    .sort((a, b) => b.score - a.score);

  return (
    <div className="px-6 py-6 space-y-4">
      <div>
        <h1 className="text-xl font-bold text-foreground">Post-op Monitoring</h1>
        <p className="text-sm text-muted-foreground">Post-operative patients sorted by NEWS2 score — highest acuity first</p>
      </div>

      {isLoading || detailQueries.isLoading ? (
        <SkeletonTable rows={6} cols={4} />
      ) : withScores.length === 0 ? (
        <EmptyState icon={Activity} title="No post-operative patients" description="Patients move here after their intervention." />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {withScores.map(({ detail }) => (
            <PatientVitalsCard key={detail.patient_id} detail={detail} />
          ))}
        </div>
      )}
    </div>
  );
}
