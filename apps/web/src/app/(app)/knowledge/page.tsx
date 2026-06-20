"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { BookOpen, FileText } from "lucide-react";
import { api } from "@/lib/api";
import { SkeletonTable } from "@/components/ui/SkeletonTable";
import { EmptyState } from "@/components/ui/EmptyState";

interface KBItem {
  id: string;
  type: "guideline" | "literature";
  title: string;
  section: string;
  source: string;
}

const SECTIONS = ["all", "surveillance", "intervention", "anticoagulation", "postop", "medical", "perioperative", "renal", "outcomes", "devices"] as const;

export default function KnowledgePage() {
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<"all" | "guideline" | "literature">("all");
  const [section, setSection] = useState("all");

  const { data, isLoading } = useQuery({
    queryKey: ["knowledge"],
    queryFn: () => api.get<KBItem[]>("/ai/knowledge"),
  });

  const filtered = (data ?? []).filter((item) => {
    if (typeFilter !== "all" && item.type !== typeFilter) return false;
    if (section !== "all" && item.section !== section) return false;
    if (search && !item.title.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const guidelines = filtered.filter((i) => i.type === "guideline").length;
  const literature = filtered.filter((i) => i.type === "literature").length;

  return (
    <div className="px-6 py-6 space-y-4">
      <div>
        <h1 className="text-xl font-bold text-foreground">Knowledge Base</h1>
        <p className="text-sm text-muted-foreground">
          Clinical guidelines and literature indexed by the AI Copilot — {guidelines} guidelines, {literature} references
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <input
          type="search"
          placeholder="Search titles…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-700 w-56"
        />
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value as typeof typeFilter)}
          className="rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-700"
        >
          <option value="all">All types</option>
          <option value="guideline">Guidelines</option>
          <option value="literature">Literature</option>
        </select>
        <select
          value={section}
          onChange={(e) => setSection(e.target.value)}
          className="rounded-md border border-border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-700"
        >
          {SECTIONS.map((s) => (
            <option key={s} value={s}>{s === "all" ? "All sections" : s.charAt(0).toUpperCase() + s.slice(1)}</option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <SkeletonTable rows={6} cols={3} />
      ) : filtered.length === 0 ? (
        <EmptyState icon={BookOpen} title="No entries found" description="Try adjusting your filters." />
      ) : (
        <div className="rounded-lg border border-border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/20 border-b border-border text-xs text-muted-foreground">
              <tr>
                <th className="text-left px-4 py-3 w-8">#</th>
                <th className="text-left px-4 py-3">Title</th>
                <th className="text-left px-4 py-3 w-28">Type</th>
                <th className="text-left px-4 py-3 w-32">Section</th>
                <th className="text-left px-4 py-3">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((item, i) => (
                <tr key={item.id} className="hover:bg-muted/10 transition-colors">
                  <td className="px-4 py-3 text-muted-foreground font-mono text-xs">{i + 1}</td>
                  <td className="px-4 py-3 font-medium text-foreground">{item.title}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1 text-xs rounded-full px-2 py-0.5 ${
                      item.type === "guideline"
                        ? "bg-indigo-900/40 text-indigo-300"
                        : "bg-amber-900/30 text-amber-300"
                    }`}>
                      {item.type === "guideline"
                        ? <BookOpen className="h-2.5 w-2.5" />
                        : <FileText className="h-2.5 w-2.5" />}
                      {item.type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-muted-foreground capitalize">{item.section || "—"}</td>
                  <td className="px-4 py-3 text-xs text-muted-foreground italic">{item.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="text-xs text-rose-400/70">
        ⚠️ Educational demo on synthetic data — not for clinical use; not medical advice.
      </p>
    </div>
  );
}
