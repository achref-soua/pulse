import { cn } from "@pulse/ui";

export type RiskLevel = "low" | "medium" | "high" | "critical";

const styles: Record<RiskLevel, string> = {
  low: "bg-emerald-900/40 text-emerald-300 border border-emerald-700/50",
  medium: "bg-amber-900/40 text-amber-300 border border-amber-700/50",
  high: "bg-orange-900/40 text-orange-300 border border-orange-700/50",
  critical: "bg-rose-900/40 text-rose-300 border border-rose-700/50",
};

const labels: Record<RiskLevel, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
  critical: "Critical",
};

interface RiskBadgeProps {
  level: RiskLevel;
  label?: string;
  className?: string;
}

export function RiskBadge({ level, label, className }: RiskBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        styles[level],
        className
      )}
    >
      {label ?? labels[level]}
    </span>
  );
}

export function news2ToRiskLevel(score: number): RiskLevel {
  if (score >= 7) return "critical";
  if (score >= 5) return "high";
  if (score >= 1) return "medium";
  return "low";
}

export function responseToRiskLevel(level: string): RiskLevel {
  if (level === "High") return "critical";
  if (level === "Medium") return "high";
  return "low";
}
