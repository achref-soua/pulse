"use client";

import { useEffect, useState } from "react";
import { useTheme } from "next-themes";

/** Resolve a CSS custom property (an "H S% L%" triplet) into an hsl() string. */
function readToken(name: string, fallback: string): string {
  if (typeof window === "undefined") return fallback;
  const raw = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return raw ? `hsl(${raw})` : fallback;
}

export interface ChartColors {
  chart: [string, string, string, string, string];
  grid: string;
  axis: string;
  tooltipBg: string;
  tooltipBorder: string;
  tooltipText: string;
}

/**
 * Reads the active theme's chart tokens from CSS so Recharts (which needs
 * literal colour strings, not classes) stays in sync with light/dark.
 * Recomputes whenever the resolved theme flips.
 */
export function useChartColors(): ChartColors {
  const { resolvedTheme } = useTheme();
  const [colors, setColors] = useState<ChartColors>(() => compute());

  useEffect(() => {
    // Next tick, after next-themes has swapped the `class` on <html>.
    const id = requestAnimationFrame(() => setColors(compute()));
    return () => cancelAnimationFrame(id);
  }, [resolvedTheme]);

  return colors;
}

function compute(): ChartColors {
  return {
    chart: [
      readToken("--chart-1", "hsl(221 83% 53%)"),
      readToken("--chart-2", "hsl(173 80% 36%)"),
      readToken("--chart-3", "hsl(32 95% 44%)"),
      readToken("--chart-4", "hsl(262 83% 58%)"),
      readToken("--chart-5", "hsl(347 77% 50%)"),
    ],
    grid: readToken("--border", "hsl(214 32% 91%)"),
    axis: readToken("--muted-foreground", "hsl(215 16% 47%)"),
    tooltipBg: readToken("--popover", "hsl(0 0% 100%)"),
    tooltipBorder: readToken("--border", "hsl(214 32% 91%)"),
    tooltipText: readToken("--popover-foreground", "hsl(222 47% 9%)"),
  };
}
