"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { RiskBadge, RiskLevel, news2ToRiskLevel } from "@/components/ui/RiskBadge";

/* ── Calculator registry ── */
const CALCULATORS = [
  { id: "rcri", label: "RCRI", fullName: "Revised Cardiac Risk Index" },
  { id: "cha2ds2vasc", label: "CHA₂DS₂-VASc", fullName: "Stroke Risk in AF" },
  { id: "hasbled", label: "HAS-BLED", fullName: "Bleeding Risk in AF" },
  { id: "news2", label: "NEWS2", fullName: "National Early Warning Score 2" },
  { id: "gas", label: "GAS", fullName: "Glasgow Aneurysm Score" },
  { id: "euroscore2", label: "EuroSCORE II", fullName: "Cardiac Surgery Mortality" },
  { id: "ifufit", label: "IFU-Fit", fullName: "Device Suitability (Anatomical)" },
] as const;

type CalcId = typeof CALCULATORS[number]["id"];

/* ── Shared checkbox field — accepts spread register() result ── */
function CheckField({ label, ...inputProps }: { label: string } & React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <label className="flex items-center gap-2 text-sm cursor-pointer">
      <input
        type="checkbox"
        {...inputProps}
        className="h-4 w-4 rounded border-border bg-card accent-indigo-500"
      />
      {label}
    </label>
  );
}

/* ── Number field — accepts spread register() result ── */
function NumberField({ label, unit, error, ...inputProps }: {
  label: string; unit?: string; error?: string;
} & React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <div className="space-y-1">
      <label className="text-xs text-muted-foreground">{label}</label>
      <div className="flex items-center gap-2">
        <input
          type="number"
          step="any"
          {...inputProps}
          className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-700"
        />
        {unit && <span className="text-xs text-muted-foreground shrink-0">{unit}</span>}
      </div>
      {error && <p className="text-xs text-rose-400">{error}</p>}
    </div>
  );
}

/* ── Result panel ── */
function ResultPanel({ result, calcId }: { result: Record<string, unknown>; calcId: CalcId }) {
  const entries = Object.entries(result);

  const level: RiskLevel =
    calcId === "news2"
      ? news2ToRiskLevel((result.total_score as number) ?? 0)
      : calcId === "rcri"
      ? (["I", "II"].includes(result.risk_class as string) ? "low" : result.risk_class === "III" ? "medium" : "high")
      : calcId === "euroscore2"
      ? (result.risk_category === "Low" ? "low" : result.risk_category === "Moderate" ? "medium" : "high")
      : (result.risk_category === "Low" ? "low" : result.risk_category === "High" ? "high" : "medium");

  return (
    <div className="rounded-lg border border-border bg-card p-5 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">Result</h3>
        <RiskBadge level={level} />
      </div>
      <dl className="space-y-2">
        {entries.map(([key, val]) => {
          if (key === "individual_scores" || key === "factors_present") {
            const sub = val as Record<string, unknown>;
            return (
              <details key={key} className="text-xs">
                <summary className="cursor-pointer text-muted-foreground capitalize">{key.replace(/_/g, " ")}</summary>
                <ul className="mt-1 ml-3 space-y-0.5">
                  {Object.entries(sub).map(([k, v]) => (
                    <li key={k} className="flex justify-between">
                      <span className="text-muted-foreground capitalize">{k.replace(/_/g, " ")}</span>
                      <span className="font-medium">{String(v)}</span>
                    </li>
                  ))}
                </ul>
              </details>
            );
          }
          return (
            <div key={key} className="flex justify-between text-sm">
              <dt className="text-muted-foreground capitalize">{key.replace(/_/g, " ")}</dt>
              <dd className="font-medium">{typeof val === "number" ? (Number.isInteger(val) ? val : val.toFixed(2)) : String(val)}</dd>
            </div>
          );
        })}
      </dl>
    </div>
  );
}

/* ── IFU-Fit Result ── */
function IFUResult({ results }: { results: Array<{ device_name: string; overall: string; criteria: Array<{ name: string; status: string; patient_value: string | number; ifu_threshold: string; note: string }>; recommended_size_note: string }> }) {
  const color = (s: string) => s === "suitable" ? "text-emerald-400" : s === "borderline" ? "text-amber-400" : "text-rose-400";
  return (
    <div className="rounded-lg border border-border bg-card divide-y divide-border">
      <div className="px-4 py-3">
        <h3 className="text-sm font-semibold">IFU-Fit Results ({results.length} devices)</h3>
      </div>
      {results.map((r) => (
        <details key={r.device_name} className="group">
          <summary className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-muted/20 list-none">
            <span className="text-sm font-medium">{r.device_name}</span>
            <span className={`text-xs font-semibold capitalize ${color(r.overall)}`}>{r.overall}</span>
          </summary>
          <div className="px-4 pb-3 space-y-1">
            {r.criteria.map((c) => (
              <div key={c.name} className="flex items-start justify-between text-xs gap-4">
                <span className="text-muted-foreground">{c.name}</span>
                <span className={`shrink-0 ${color(c.status)}`}>{c.status} (pt: {c.patient_value} | IFU: {c.ifu_threshold})</span>
              </div>
            ))}
            {r.recommended_size_note && <p className="text-xs text-muted-foreground italic mt-1">{r.recommended_size_note}</p>}
          </div>
        </details>
      ))}
    </div>
  );
}

/* ── Zod schemas for each calculator ── */
const rcriSchema = z.object({
  high_risk_surgery: z.boolean(),
  ischemic_heart_disease: z.boolean(),
  congestive_heart_failure: z.boolean(),
  cerebrovascular_disease: z.boolean(),
  insulin_dependent_diabetes: z.boolean(),
  preop_creatinine_gt_2: z.boolean(),
});

const cha2dsSchema = z.object({
  congestive_heart_failure: z.boolean(),
  hypertension: z.boolean(),
  age_75_or_over: z.boolean(),
  diabetes_mellitus: z.boolean(),
  stroke_or_tia: z.boolean(),
  vascular_disease: z.boolean(),
  age_65_to_74: z.boolean(),
  female_sex: z.boolean(),
});

const hasBledSchema = z.object({
  hypertension_uncontrolled: z.boolean(),
  renal_dysfunction: z.boolean(),
  liver_dysfunction: z.boolean(),
  stroke_history: z.boolean(),
  bleeding_predisposition: z.boolean(),
  labile_inr: z.boolean(),
  elderly: z.boolean(),
  antiplatelet_or_nsaid: z.boolean(),
  alcohol: z.boolean(),
});

const news2Schema = z.object({
  respiration_rate: z.number().int().min(1),
  spo2: z.number().min(50).max(100),
  on_supplemental_oxygen: z.boolean(),
  systolic_bp: z.number().int().min(40),
  heart_rate: z.number().int().min(20),
  consciousness: z.enum(["A", "V", "P", "U"]),
  temperature: z.number().min(30).max(44),
});

const gasSchema = z.object({
  age: z.number().int().min(0).max(130),
  shock: z.boolean(),
  myocardial_disease: z.boolean(),
  cerebrovascular_disease: z.boolean(),
  renal_disease: z.boolean(),
});

const euroscoreSchema = z.object({
  age: z.number().int().min(18).max(120),
  female: z.boolean(),
  renal_dysfunction: z.enum(["none", "moderate", "dialysis"]),
  extracardiac_arteriopathy: z.boolean(),
  poor_mobility: z.boolean(),
  previous_cardiac_surgery: z.boolean(),
  chronic_lung_disease: z.boolean(),
  active_endocarditis: z.boolean(),
  critical_preop_state: z.boolean(),
  diabetes_on_insulin: z.boolean(),
  nyha_class: z.coerce.number().int().min(1).max(4),
  ccs_angina: z.coerce.number().int().min(0).max(4),
  ejection_fraction_pct: z.number().min(1).max(100),
  recent_mi: z.boolean(),
  pulmonary_hypertension: z.enum(["none", "moderate", "severe"]),
  emergency: z.boolean(),
  other_than_isolated_cabg: z.boolean(),
  thoracic_aorta_surgery: z.boolean(),
});

const ifufitSchema = z.object({
  neck_length_mm: z.number().min(0),
  neck_angulation_deg: z.number().min(0).max(180),
  neck_diameter_mm: z.number().min(5).max(50),
  iliac_access_min_mm: z.number().min(3).max(30),
  max_diameter_mm: z.number().min(10).max(150),
});

type RcriForm = z.infer<typeof rcriSchema>;
type Cha2dsForm = z.infer<typeof cha2dsSchema>;
type HasBledForm = z.infer<typeof hasBledSchema>;
type News2Form = z.infer<typeof news2Schema>;
type GasForm = z.infer<typeof gasSchema>;
type EuroscoreForm = z.infer<typeof euroscoreSchema>;
type IfufitForm = z.infer<typeof ifufitSchema>;

/* ── Individual calculator forms ── */
function RCRIForm({ onResult }: { onResult: (r: Record<string, unknown>) => void }) {
  const { register, handleSubmit } = useForm<RcriForm>({ resolver: zodResolver(rcriSchema) });
  const [loading, setLoading] = useState(false);
  async function onSubmit(data: RcriForm) {
    setLoading(true);
    const r = await api.post<Record<string, unknown>>("/risk/rcri", data);
    onResult(r);
    setLoading(false);
  }
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      {([
        ["high_risk_surgery", "High-risk surgery"],
        ["ischemic_heart_disease", "Ischemic heart disease"],
        ["congestive_heart_failure", "Congestive heart failure"],
        ["cerebrovascular_disease", "Cerebrovascular disease"],
        ["insulin_dependent_diabetes", "Insulin-dependent diabetes"],
        ["preop_creatinine_gt_2", "Pre-op creatinine > 2 mg/dL (>177 µmol/L)"],
      ] as const).map(([f, l]) => <CheckField key={f} label={l} {...register(f)} />)}
      <button type="submit" disabled={loading} className="mt-2 w-full rounded-md bg-indigo-700 hover:bg-indigo-600 text-white py-2 text-sm font-medium transition-colors disabled:opacity-60">
        {loading ? "Computing…" : "Calculate RCRI"}
      </button>
    </form>
  );
}

function CHA2DS2Form({ onResult }: { onResult: (r: Record<string, unknown>) => void }) {
  const { register, handleSubmit } = useForm<Cha2dsForm>({ resolver: zodResolver(cha2dsSchema) });
  const [loading, setLoading] = useState(false);
  async function onSubmit(data: Cha2dsForm) {
    setLoading(true);
    const r = await api.post<Record<string, unknown>>("/risk/cha2ds2-vasc", data);
    onResult(r);
    setLoading(false);
  }
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      {([
        ["congestive_heart_failure", "Congestive heart failure (1pt)"],
        ["hypertension", "Hypertension (1pt)"],
        ["age_75_or_over", "Age ≥ 75 (2pts)"],
        ["diabetes_mellitus", "Diabetes mellitus (1pt)"],
        ["stroke_or_tia", "Stroke or TIA (2pts)"],
        ["vascular_disease", "Vascular disease (1pt)"],
        ["age_65_to_74", "Age 65–74 (1pt)"],
        ["female_sex", "Female sex (1pt)"],
      ] as const).map(([f, l]) => <CheckField key={f} label={l} {...register(f)} />)}
      <button type="submit" disabled={loading} className="mt-2 w-full rounded-md bg-indigo-700 hover:bg-indigo-600 text-white py-2 text-sm font-medium transition-colors disabled:opacity-60">
        {loading ? "Computing…" : "Calculate CHA₂DS₂-VASc"}
      </button>
    </form>
  );
}

function HASBLEDForm({ onResult }: { onResult: (r: Record<string, unknown>) => void }) {
  const { register, handleSubmit } = useForm<HasBledForm>({ resolver: zodResolver(hasBledSchema) });
  const [loading, setLoading] = useState(false);
  async function onSubmit(data: HasBledForm) {
    setLoading(true);
    const r = await api.post<Record<string, unknown>>("/risk/has-bled", data);
    onResult(r);
    setLoading(false);
  }
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      {([
        ["hypertension_uncontrolled", "Uncontrolled hypertension (SBP > 160)"],
        ["renal_dysfunction", "Renal dysfunction"],
        ["liver_dysfunction", "Liver dysfunction"],
        ["stroke_history", "Prior stroke"],
        ["bleeding_predisposition", "Prior bleeding / anemia / thrombocytopenia"],
        ["labile_inr", "Labile INR (< 60% time in therapeutic range)"],
        ["elderly", "Age > 65"],
        ["antiplatelet_or_nsaid", "Antiplatelet drug or NSAID"],
        ["alcohol", "Alcohol use (≥ 8 drinks/week)"],
      ] as const).map(([f, l]) => <CheckField key={f} label={l} {...register(f)} />)}
      <button type="submit" disabled={loading} className="mt-2 w-full rounded-md bg-indigo-700 hover:bg-indigo-600 text-white py-2 text-sm font-medium transition-colors disabled:opacity-60">
        {loading ? "Computing…" : "Calculate HAS-BLED"}
      </button>
    </form>
  );
}

function NEWS2Form({ onResult }: { onResult: (r: Record<string, unknown>) => void }) {
  const { register, handleSubmit, formState: { errors } } = useForm<News2Form>({ resolver: zodResolver(news2Schema) });
  const [loading, setLoading] = useState(false);
  async function onSubmit(data: News2Form) {
    setLoading(true);
    const r = await api.post<Record<string, unknown>>("/risk/news2", data);
    onResult(r);
    setLoading(false);
  }
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <NumberField label="Respiration rate (br/min)" {...register("respiration_rate", { valueAsNumber: true })} error={errors.respiration_rate?.message} />
      <NumberField label="SpO₂ (%)" {...register("spo2", { valueAsNumber: true })} error={errors.spo2?.message} />
      <CheckField label="On supplemental oxygen" {...register("on_supplemental_oxygen")} />
      <NumberField label="Systolic BP (mmHg)" {...register("systolic_bp", { valueAsNumber: true })} error={errors.systolic_bp?.message} />
      <NumberField label="Heart rate (bpm)" {...register("heart_rate", { valueAsNumber: true })} error={errors.heart_rate?.message} />
      <div className="space-y-1">
        <label className="text-xs text-muted-foreground">Consciousness (AVPU)</label>
        <select {...register("consciousness")} className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-indigo-700">
          <option value="A">A — Alert</option>
          <option value="V">V — Voice</option>
          <option value="P">P — Pain</option>
          <option value="U">U — Unresponsive</option>
        </select>
      </div>
      <NumberField label="Temperature (°C)" {...register("temperature", { valueAsNumber: true })} error={errors.temperature?.message} />
      <button type="submit" disabled={loading} className="mt-2 w-full rounded-md bg-indigo-700 hover:bg-indigo-600 text-white py-2 text-sm font-medium transition-colors disabled:opacity-60">
        {loading ? "Computing…" : "Calculate NEWS2"}
      </button>
    </form>
  );
}

function GASForm({ onResult }: { onResult: (r: Record<string, unknown>) => void }) {
  const { register, handleSubmit, formState: { errors } } = useForm<GasForm>({ resolver: zodResolver(gasSchema) });
  const [loading, setLoading] = useState(false);
  async function onSubmit(data: GasForm) {
    setLoading(true);
    const r = await api.post<Record<string, unknown>>("/risk/gas", data);
    onResult(r);
    setLoading(false);
  }
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <NumberField label="Age (years)" {...register("age", { valueAsNumber: true })} error={errors.age?.message} />
      <CheckField label="Haemodynamic shock" {...register("shock")} />
      <CheckField label="Myocardial disease" {...register("myocardial_disease")} />
      <CheckField label="Cerebrovascular disease" {...register("cerebrovascular_disease")} />
      <CheckField label="Renal disease" {...register("renal_disease")} />
      <button type="submit" disabled={loading} className="mt-2 w-full rounded-md bg-indigo-700 hover:bg-indigo-600 text-white py-2 text-sm font-medium transition-colors disabled:opacity-60">
        {loading ? "Computing…" : "Calculate GAS"}
      </button>
    </form>
  );
}

function EuroscoreForm({ onResult }: { onResult: (r: Record<string, unknown>) => void }) {
  const { register, handleSubmit, formState: { errors } } = useForm<EuroscoreForm>({ resolver: zodResolver(euroscoreSchema) });
  const [loading, setLoading] = useState(false);
  async function onSubmit(data: EuroscoreForm) {
    setLoading(true);
    const r = await api.post<Record<string, unknown>>("/risk/euroscore2", data);
    onResult(r);
    setLoading(false);
  }
  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <NumberField label="Age (years)" {...register("age", { valueAsNumber: true })} error={errors.age?.message} />
      <CheckField label="Female sex" {...register("female")} />
      <div className="space-y-1">
        <label className="text-xs text-muted-foreground">Renal dysfunction</label>
        <select {...register("renal_dysfunction")} className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-indigo-700">
          <option value="none">None</option>
          <option value="moderate">Moderate (creatinine &gt; 200 µmol/L)</option>
          <option value="dialysis">On dialysis</option>
        </select>
      </div>
      {([
        ["extracardiac_arteriopathy", "Extracardiac arteriopathy"],
        ["poor_mobility", "Poor mobility"],
        ["previous_cardiac_surgery", "Previous cardiac surgery"],
        ["chronic_lung_disease", "Chronic lung disease"],
        ["active_endocarditis", "Active endocarditis"],
        ["critical_preop_state", "Critical pre-op state"],
        ["diabetes_on_insulin", "Diabetes on insulin"],
        ["recent_mi", "Recent MI (within 90 days)"],
        ["emergency", "Emergency surgery"],
        ["other_than_isolated_cabg", "Non-isolated CABG procedure"],
        ["thoracic_aorta_surgery", "Thoracic aorta surgery"],
      ] as const).map(([f, l]) => <CheckField key={f} label={l} {...register(f)} />)}
      <NumberField label="NYHA class (1–4)" {...register("nyha_class", { valueAsNumber: true })} error={errors.nyha_class?.message} />
      <NumberField label="CCS angina (0–4)" {...register("ccs_angina", { valueAsNumber: true })} error={errors.ccs_angina?.message} />
      <NumberField label="Ejection fraction (%)" {...register("ejection_fraction_pct", { valueAsNumber: true })} error={errors.ejection_fraction_pct?.message} />
      <div className="space-y-1">
        <label className="text-xs text-muted-foreground">Pulmonary hypertension</label>
        <select {...register("pulmonary_hypertension")} className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-indigo-700">
          <option value="none">None</option>
          <option value="moderate">Moderate (31–55 mmHg)</option>
          <option value="severe">Severe (&gt; 55 mmHg)</option>
        </select>
      </div>
      <button type="submit" disabled={loading} className="mt-2 w-full rounded-md bg-indigo-700 hover:bg-indigo-600 text-white py-2 text-sm font-medium transition-colors disabled:opacity-60">
        {loading ? "Computing…" : "Calculate EuroSCORE II"}
      </button>
    </form>
  );
}

interface Device {
  id: string; manufacturer: string; name: string; indication: string; sheath_fr: number;
  ifu_proximal_min_mm: number; ifu_proximal_max_mm: number;
  ifu_min_neck_length_mm: number; ifu_max_neck_angulation_deg: number;
  ifu_iliac_min_mm: number; ifu_iliac_max_mm: number;
  ifu_distal_min_mm: number; ifu_distal_max_mm: number;
}

function IFUFitForm({ onResult }: { onResult: (r: Record<string, unknown>) => void }) {
  const { register, handleSubmit, formState: { errors } } = useForm<IfufitForm>({ resolver: zodResolver(ifufitSchema) });
  const [loading, setLoading] = useState(false);
  const [selectedDevices, setSelectedDevices] = useState<string[]>([]);

  const { data: devices } = useQuery({
    queryKey: ["devices"],
    queryFn: () => api.get<Device[]>("/devices"),
  });

  async function onSubmit(data: IfufitForm) {
    if (selectedDevices.length === 0) return;
    setLoading(true);
    const devObjs = (devices ?? [])
      .filter((d) => selectedDevices.includes(d.id))
      .map((d) => ({
        name: d.name,
        ifu_min_neck_length_mm: d.ifu_min_neck_length_mm,
        ifu_max_neck_angulation_deg: d.ifu_max_neck_angulation_deg,
        ifu_proximal_min_mm: d.ifu_proximal_min_mm,
        ifu_proximal_max_mm: d.ifu_proximal_max_mm,
        ifu_iliac_min_mm: d.ifu_iliac_min_mm,
        ifu_iliac_max_mm: d.ifu_iliac_max_mm,
        ifu_distal_min_mm: d.ifu_distal_min_mm,
        ifu_distal_max_mm: d.ifu_distal_max_mm,
      }));
    const r = await api.post<unknown[]>("/risk/ifu-fit", { ...data, distal_landing_diameter_mm: null, devices: devObjs });
    onResult({ results: r } as Record<string, unknown>);
    setLoading(false);
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <NumberField label="Neck length (mm)" unit="mm" {...register("neck_length_mm", { valueAsNumber: true })} error={errors.neck_length_mm?.message} />
      <NumberField label="Neck angulation (°)" unit="°" {...register("neck_angulation_deg", { valueAsNumber: true })} error={errors.neck_angulation_deg?.message} />
      <NumberField label="Neck diameter (mm)" unit="mm" {...register("neck_diameter_mm", { valueAsNumber: true })} error={errors.neck_diameter_mm?.message} />
      <NumberField label="Min iliac access (mm)" unit="mm" {...register("iliac_access_min_mm", { valueAsNumber: true })} error={errors.iliac_access_min_mm?.message} />
      <NumberField label="Max aneurysm diameter (mm)" unit="mm" {...register("max_diameter_mm", { valueAsNumber: true })} error={errors.max_diameter_mm?.message} />
      <div className="space-y-2">
        <p className="text-xs text-muted-foreground">Devices to evaluate (select ≥ 1)</p>
        {!devices ? (
          <p className="text-xs text-muted-foreground">Loading devices…</p>
        ) : (
          <div className="space-y-1 max-h-48 overflow-y-auto pr-1">
            {devices.map((d) => (
              <label key={d.id} className="flex items-center gap-2 text-xs cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedDevices.includes(d.id)}
                  onChange={(e) =>
                    setSelectedDevices((prev) =>
                      e.target.checked ? [...prev, d.id] : prev.filter((x) => x !== d.id)
                    )
                  }
                  className="h-3.5 w-3.5 rounded border-border accent-indigo-500"
                />
                <span>{d.name} <span className="text-muted-foreground">({d.indication})</span></span>
              </label>
            ))}
          </div>
        )}
      </div>
      <button
        type="submit"
        disabled={loading || selectedDevices.length === 0}
        className="mt-2 w-full rounded-md bg-indigo-700 hover:bg-indigo-600 text-white py-2 text-sm font-medium transition-colors disabled:opacity-60"
      >
        {loading ? "Computing…" : "Evaluate IFU Fit"}
      </button>
    </form>
  );
}

/* ── Main page ── */
export default function RiskPage() {
  const [activeCalc, setActiveCalc] = useState<CalcId>("rcri");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  function handleResult(r: Record<string, unknown>) {
    setResult(r);
  }

  return (
    <div className="px-6 py-6">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-foreground">Risk Tools</h1>
        <p className="text-sm text-muted-foreground">Clinical risk calculators — results computed by the backend engine</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calculator picker + form */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex flex-wrap gap-2">
            {CALCULATORS.map((c) => (
              <button
                key={c.id}
                onClick={() => { setActiveCalc(c.id); setResult(null); }}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                  activeCalc === c.id
                    ? "bg-indigo-700 text-white"
                    : "bg-muted/30 text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                }`}
              >
                {c.label}
              </button>
            ))}
          </div>
          <div className="rounded-lg border border-border bg-card p-5">
            <div className="mb-4">
              <h2 className="text-sm font-semibold text-foreground">
                {CALCULATORS.find((c) => c.id === activeCalc)?.fullName}
              </h2>
              <p className="text-xs text-muted-foreground mt-0.5">
                Scores computed server-side — never re-derived in the browser.
              </p>
            </div>
            {activeCalc === "rcri" && <RCRIForm onResult={handleResult} />}
            {activeCalc === "cha2ds2vasc" && <CHA2DS2Form onResult={handleResult} />}
            {activeCalc === "hasbled" && <HASBLEDForm onResult={handleResult} />}
            {activeCalc === "news2" && <NEWS2Form onResult={handleResult} />}
            {activeCalc === "gas" && <GASForm onResult={handleResult} />}
            {activeCalc === "euroscore2" && <EuroscoreForm onResult={handleResult} />}
            {activeCalc === "ifufit" && <IFUFitForm onResult={handleResult} />}
          </div>
        </div>

        {/* Result panel */}
        <div>
          {result ? (
            activeCalc === "ifufit" ? (
              <IFUResult results={(result.results as Array<{ device_name: string; overall: string; criteria: Array<{ name: string; status: string; patient_value: string | number; ifu_threshold: string; note: string }>; recommended_size_note: string }>) ?? []} />
            ) : (
              <ResultPanel result={result} calcId={activeCalc} />
            )
          ) : (
            <div className="rounded-lg border border-dashed border-border bg-card/50 p-8 text-center">
              <p className="text-sm text-muted-foreground">Fill in the form and submit to see the result here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
