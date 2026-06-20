"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Cpu, X } from "lucide-react";
import { api } from "@/lib/api";
import { EmptyState } from "@/components/ui/EmptyState";
import { SkeletonCard } from "@/components/ui/SkeletonTable";

interface Device {
  id: string;
  manufacturer: string;
  name: string;
  indication: string;
  sheath_fr: number;
  ifu_proximal_min_mm: number;
  ifu_proximal_max_mm: number;
  ifu_distal_min_mm: number;
  ifu_distal_max_mm: number;
  ifu_length_options_mm: number[];
  ifu_min_neck_length_mm: number;
  ifu_max_neck_angulation_deg: number;
  ifu_iliac_min_mm: number;
  ifu_iliac_max_mm: number;
  contraindications: string[];
  deployment_steps: string[];
}

function IndicationBadge({ indication }: { indication: string }) {
  const colors =
    indication === "EVAR"
      ? "bg-indigo-900/40 text-indigo-300 border-indigo-700/40"
      : "bg-purple-900/40 text-purple-300 border-purple-700/40";
  return (
    <span className={`text-xs font-medium rounded-full border px-2 py-0.5 ${colors}`}>
      {indication}
    </span>
  );
}

function DeviceModal({
  device,
  onClose,
  onMatchToPatient,
}: {
  device: Device;
  onClose: () => void;
  onMatchToPatient: (device: Device) => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-xl border border-border bg-card shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 flex items-start justify-between bg-card border-b border-border px-6 py-4 gap-4">
          <div>
            <h2 className="text-base font-bold text-foreground">{device.name}</h2>
            <p className="text-xs text-muted-foreground mt-0.5">{device.manufacturer}</p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <IndicationBadge indication={device.indication} />
            <button onClick={onClose} className="text-muted-foreground hover:text-foreground transition-colors">
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        <div className="px-6 py-5 space-y-5">
          {/* IFU specs */}
          <section>
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
              IFU Envelope
            </h3>
            <dl className="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-3">
              {([
                ["Proximal diameter", `${device.ifu_proximal_min_mm}–${device.ifu_proximal_max_mm} mm`],
                ["Distal diameter", `${device.ifu_distal_min_mm}–${device.ifu_distal_max_mm} mm`],
                ["Min neck length", `${device.ifu_min_neck_length_mm} mm`],
                ["Max neck angulation", `${device.ifu_max_neck_angulation_deg}°`],
                ["Iliac access", `${device.ifu_iliac_min_mm}–${device.ifu_iliac_max_mm} mm`],
                ["Sheath size", `${device.sheath_fr} Fr`],
              ] as [string, string][]).map(([label, value]) => (
                <div key={label} className="flex flex-col gap-0.5">
                  <dt className="text-xs text-muted-foreground">{label}</dt>
                  <dd className="text-sm font-medium text-foreground">{value}</dd>
                </div>
              ))}
            </dl>
            {device.ifu_length_options_mm.length > 0 && (
              <div className="mt-3 flex flex-col gap-0.5">
                <dt className="text-xs text-muted-foreground">Length options</dt>
                <dd className="text-sm font-medium text-foreground">
                  {device.ifu_length_options_mm.join(", ")} mm
                </dd>
              </div>
            )}
          </section>

          {/* Contraindications */}
          {device.contraindications.length > 0 && (
            <section>
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                Contraindications
              </h3>
              <ul className="space-y-1.5">
                {device.contraindications.map((c, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-foreground/80">
                    <span className="mt-1 h-1.5 w-1.5 rounded-full bg-rose-400 shrink-0" />
                    {c}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Deployment steps */}
          {device.deployment_steps.length > 0 && (
            <section>
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
                Deployment Steps
              </h3>
              <ol className="space-y-2">
                {device.deployment_steps.map((step, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-foreground/80">
                    <span className="shrink-0 flex h-5 w-5 items-center justify-center rounded-full bg-indigo-900/50 text-xs font-medium text-indigo-300">
                      {i + 1}
                    </span>
                    {step}
                  </li>
                ))}
              </ol>
            </section>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-card border-t border-border px-6 py-4 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="text-sm px-4 py-2 rounded-md border border-border hover:bg-muted/30 transition-colors"
          >
            Close
          </button>
          <button
            onClick={() => { onMatchToPatient(device); onClose(); }}
            className="text-sm px-4 py-2 rounded-md bg-indigo-700 hover:bg-indigo-600 text-white transition-colors"
          >
            Match to patient →
          </button>
        </div>
      </div>
    </div>
  );
}

function DeviceCard({ device, onClick }: { device: Device; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="text-left rounded-lg border border-border bg-card p-4 hover:border-indigo-700/50 hover:bg-indigo-900/10 transition-colors space-y-3 w-full"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-xs text-muted-foreground truncate">{device.manufacturer}</p>
          <p className="text-sm font-semibold text-foreground leading-tight mt-0.5">{device.name}</p>
        </div>
        <IndicationBadge indication={device.indication} />
      </div>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-1.5">
        {([
          ["Proximal Ø", `${device.ifu_proximal_min_mm}–${device.ifu_proximal_max_mm} mm`],
          ["Neck ≥", `${device.ifu_min_neck_length_mm} mm`],
          ["Angulation ≤", `${device.ifu_max_neck_angulation_deg}°`],
          ["Sheath", `${device.sheath_fr} Fr`],
        ] as [string, string][]).map(([label, value]) => (
          <div key={label} className="flex flex-col gap-0">
            <dt className="text-xs text-muted-foreground">{label}</dt>
            <dd className="text-xs font-medium text-foreground">{value}</dd>
          </div>
        ))}
      </dl>
      <p className="text-xs text-indigo-400 font-medium">View IFU specs →</p>
    </button>
  );
}

export default function DevicesPage() {
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
  const [filter, setFilter] = useState<"all" | "EVAR" | "TEVAR">("all");

  const { data: devices, isLoading } = useQuery({
    queryKey: ["devices"],
    queryFn: () => api.get<Device[]>("/devices"),
  });

  const filtered = devices?.filter(
    (d) => filter === "all" || d.indication === filter
  ) ?? [];

  function handleMatchToPatient(device: Device) {
    window.location.href = `/risk?calc=ifufit&device=${device.id}`;
  }

  return (
    <div className="px-6 py-6 space-y-4">
      <div>
        <h1 className="text-xl font-bold text-foreground">Device Catalog</h1>
        <p className="text-sm text-muted-foreground">
          Stent-graft devices with IFU specifications for anatomical fit evaluation
        </p>
      </div>

      <div className="flex gap-2">
        {(["all", "EVAR", "TEVAR"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              filter === f
                ? "bg-indigo-700 text-white"
                : "bg-muted/30 text-muted-foreground hover:bg-muted/50"
            }`}
          >
            {f === "all" ? "All devices" : f}
          </button>
        ))}
        {devices && (
          <span className="ml-auto text-xs text-muted-foreground self-center">
            {filtered.length} device{filtered.length !== 1 ? "s" : ""}
          </span>
        )}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState icon={Cpu} title="No devices found" description="No catalog devices match the current filter." />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((d) => (
            <DeviceCard key={d.id} device={d} onClick={() => setSelectedDevice(d)} />
          ))}
        </div>
      )}

      {selectedDevice && (
        <DeviceModal
          device={selectedDevice}
          onClose={() => setSelectedDevice(null)}
          onMatchToPatient={handleMatchToPatient}
        />
      )}
    </div>
  );
}
