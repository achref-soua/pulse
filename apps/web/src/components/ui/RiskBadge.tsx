import { cn } from "@pulse/ui";

export type RiskLevel = "low" | "medium" | "high" | "critical";

// Clinical severity coding needs four distinct hues; each carries an explicit
// light and dark treatment so it reads correctly in both themes.
const styles: Record<RiskLevel, string> = {
  low: "border border-emerald-600/20 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-400",
  medium: "border border-amber-600/20 bg-amber-50 text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-400",
  high: "border border-orange-600/20 bg-orange-50 text-orange-700 dark:border-orange-500/30 dark:bg-orange-500/10 dark:text-orange-400",
  critical: "border border-rose-600/20 bg-rose-50 text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-400",
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
