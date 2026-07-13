"use client";

import { useQuery } from "@tanstack/react-query";
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
import { BarChart2 } from "lucide-react";
import { api } from "@/lib/api";
import { useChartColors } from "@/lib/chartTheme";

interface Overview {
  total: number;
  by_phase: Record<string, number>;
  by_intervention: Record<string, number>;
  by_aneurysm_type: Record<string, number>;
  by_sex: Record<string, number>;
  by_age_band: Record<string, number>;
  by_diameter_band: Record<string, number>;
}

const PHASE_ORDER = ["pre", "intra", "post"];
const AGE_ORDER = ["<60", "60–69", "70–79", "≥80"];
const DIAMETER_ORDER = ["<50", "50–55", "55–60", "≥60"];

function toData(rec: Record<string, number> | undefined, order?: string[]) {
  const entries = Object.entries(rec ?? {});
  if (order) entries.sort((a, b) => order.indexOf(a[0]) - order.indexOf(b[0]));
  return entries.map(([name, value]) => ({ name, value }));
}

export default function AnalyticsPage() {
  const cc = useChartColors();
  const { data, isLoading } = useQuery({
    queryKey: ["analytics-overview"],
    queryFn: () => api.get<Overview>("/analytics/overview"),
  });

  const tooltipStyle = {
    backgroundColor: cc.tooltipBg,
    border: `1px solid ${cc.tooltipBorder}`,
    borderRadius: 8,
    color: cc.tooltipText,
    fontSize: 12,
  };

  const diameter = toData(data?.by_diameter_band, DIAMETER_ORDER);
  const age = toData(data?.by_age_band, AGE_ORDER);
  const phase = toData(data?.by_phase, PHASE_ORDER);
  const intervention = toData(data?.by_intervention);
  const aneurysm = toData(data?.by_aneurysm_type);
  const sex = toData(data?.by_sex);

  return (
    <div className="space-y-4 px-6 py-6">
      <div className="flex items-center gap-2">
        <BarChart2 className="h-5 w-5 text-primary" />
        <div>
          <h1 className="text-xl font-bold text-foreground">Cohort Analytics</h1>
          <p className="text-sm text-muted-foreground">
            {isLoading ? "Loading…" : `${data?.total ?? 0} synthetic patients`}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <ChartCard title="Max Aneurysm Diameter (mm)" loading={isLoading}>
          <BarChart data={diameter} margin={{ top: 4, right: 4, bottom: 0, left: -22 }}>
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: cc.axis }} />
            <YAxis tick={{ fontSize: 10, fill: cc.axis }} />
            <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: cc.axis, fontSize: 11 }} />
            <Bar dataKey="value" fill={cc.chart[0]} radius={[3, 3, 0, 0]} />
          </BarChart>
        </ChartCard>

        <ChartCard title="Age Distribution" loading={isLoading}>
          <BarChart data={age} margin={{ top: 4, right: 4, bottom: 0, left: -22 }}>
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: cc.axis }} />
            <YAxis tick={{ fontSize: 10, fill: cc.axis }} />
            <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: cc.axis, fontSize: 11 }} />
            <Bar dataKey="value" fill={cc.chart[1]} radius={[3, 3, 0, 0]} />
          </BarChart>
        </ChartCard>

        <ChartCard title="Phase Funnel" loading={isLoading}>
          <BarChart data={phase} layout="vertical" margin={{ top: 4, right: 8, bottom: 0, left: 20 }}>
            <XAxis type="number" hide />
            <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: cc.axis }} width={48} />
            <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: cc.axis, fontSize: 11 }} />
            <Bar dataKey="value" radius={[0, 3, 3, 0]}>
              {phase.map((_, i) => (
                <Cell key={i} fill={cc.chart[i % cc.chart.length]} />
              ))}
            </Bar>
          </BarChart>
        </ChartCard>

        <ChartCard title="Planned Intervention" loading={isLoading}>
          <PieChart>
            <Pie data={intervention} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={64}>
              {intervention.map((_, i) => (
                <Cell key={i} fill={cc.chart[i % cc.chart.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: cc.axis, fontSize: 11 }} />
          </PieChart>
        </ChartCard>

        <ChartCard title="Aneurysm Type" loading={isLoading}>
          <BarChart data={aneurysm} margin={{ top: 4, right: 4, bottom: 0, left: -22 }}>
            <XAxis dataKey="name" tick={{ fontSize: 9, fill: cc.axis }} />
            <YAxis tick={{ fontSize: 10, fill: cc.axis }} />
            <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: cc.axis, fontSize: 11 }} />
            <Bar dataKey="value" fill={cc.chart[2]} radius={[3, 3, 0, 0]} />
          </BarChart>
        </ChartCard>

        <ChartCard title="Sex" loading={isLoading}>
          <PieChart>
            <Pie data={sex} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={64}>
              {sex.map((_, i) => (
                <Cell key={i} fill={cc.chart[i % cc.chart.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: cc.axis, fontSize: 11 }} />
          </PieChart>
        </ChartCard>
      </div>
    </div>
  );
}

function ChartCard({
  title,
  loading,
  children,
}: {
  title: string;
  loading: boolean;
  children: React.ReactElement;
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <h2 className="mb-3 text-sm font-semibold text-foreground">{title}</h2>
      {loading ? (
        <div className="h-[180px] animate-pulse rounded bg-muted/30" />
      ) : (
        <ResponsiveContainer width="100%" height={180}>
          {children}
        </ResponsiveContainer>
      )}
    </div>
  );
}
