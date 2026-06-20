import { cn } from "@pulse/ui";

interface AnatomyField {
  label: string;
  value: string | number | null | undefined;
  unit?: string;
  highlight?: boolean;
}

interface AnatomyCardProps {
  aneurysmType: string | null;
  location: string | null;
  maxDiameterMm: number | null;
  neckLengthMm: number | null;
  neckAngulationDeg: number | null;
  neckDiameterMm: number | null;
  iliacAccessMinMm: number | null;
  iliacAccessMaxMm: number | null;
  tortuosity: string | null;
  ctScanDate: string | null;
  className?: string;
}

function Field({ label, value, unit, highlight }: AnatomyField) {
  const displayValue =
    value === null || value === undefined ? (
      <span className="text-muted-foreground italic">N/A</span>
    ) : (
      <span className={cn("font-medium", highlight && "text-amber-300")}>
        {value}
        {unit && <span className="text-muted-foreground ml-0.5 text-xs">{unit}</span>}
      </span>
    );
  return (
    <div className="flex flex-col gap-0.5">
      <dt className="text-xs text-muted-foreground uppercase tracking-wide">{label}</dt>
      <dd className="text-sm">{displayValue}</dd>
    </div>
  );
}

export function AnatomyCard({
  aneurysmType,
  location,
  maxDiameterMm,
  neckLengthMm,
  neckAngulationDeg,
  neckDiameterMm,
  iliacAccessMinMm,
  iliacAccessMaxMm,
  tortuosity,
  ctScanDate,
  className,
}: AnatomyCardProps) {
  return (
    <div className={cn("rounded-lg border border-border bg-card p-4", className)}>
      <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-indigo-400 inline-block" />
        Aortic Anatomy
      </h3>
      <dl className="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-3">
        <Field label="Type" value={aneurysmType} />
        <Field label="Location" value={location} />
        <Field
          label="Max Diameter"
          value={maxDiameterMm}
          unit="mm"
          highlight={maxDiameterMm != null && maxDiameterMm >= 55}
        />
        <Field label="Neck Length" value={neckLengthMm} unit="mm" />
        <Field
          label="Neck Angulation"
          value={neckAngulationDeg}
          unit="°"
          highlight={neckAngulationDeg != null && neckAngulationDeg > 60}
        />
        <Field label="Neck Diameter" value={neckDiameterMm} unit="mm" />
        <Field label="Iliac Access (min)" value={iliacAccessMinMm} unit="mm" />
        <Field label="Iliac Access (max)" value={iliacAccessMaxMm} unit="mm" />
        <Field label="Tortuosity" value={tortuosity} />
        <Field label="CT Scan Date" value={ctScanDate ?? undefined} />
      </dl>
    </div>
  );
}
