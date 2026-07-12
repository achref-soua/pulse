import Link from "next/link";
import {
  Activity,
  ArrowRight,
  BrainCircuit,
  ClipboardList,
  Cpu,
  Database,
  Github,
  LineChart,
  Lock,
  ShieldCheck,
  Sparkles,
  Stethoscope,
} from "lucide-react";
import { Badge, Button } from "@pulse/ui";
import { PulseLogo } from "@/components/brand/PulseLogo";
import { ThemeToggle } from "@/components/ui/ThemeToggle";

export const metadata = {
  title: "Pulse — Aortic & endovascular surgery intelligence",
  description:
    "An open-source clinical decision-support workspace for aortic and endovascular surgery: unified patient records, validated risk scoring, IFU device matching, and a grounded AI copilot — on fully synthetic data.",
};

const GITHUB = "https://github.com/achref-soua/pulse";

const WORKFLOW = [
  { n: "01", label: "Intake", icon: ClipboardList, text: "Unify anatomy, comorbidities, labs and vitals into one coherent patient record." },
  { n: "02", label: "Risk", icon: ShieldCheck, text: "Score operative risk with seven validated, unit-tested calculators." },
  { n: "03", label: "Plan", icon: Cpu, text: "Match anatomy against the stent-graft catalogue on real IFU envelopes." },
  { n: "04", label: "Monitor", icon: Activity, text: "Track post-op NEWS2 trends and surface the sickest patients first." },
];

const FEATURES = [
  { icon: Stethoscope, title: "Unified patient record", text: "Anatomy, comorbidities, labs, medications, vitals and a full note timeline — one clinical picture per patient." },
  { icon: ShieldCheck, title: "Validated risk engine", text: "RCRI, EuroSCORE II, CHA₂DS₂-VASc, HAS-BLED, NEWS2, GAS and IFU-fit — deterministic and tested against published references." },
  { icon: Cpu, title: "IFU device matching", text: "Rank stent-grafts against the patient's neck, angulation and iliac access on each device's real instructions-for-use." },
  { icon: BrainCircuit, title: "Grounded AI copilot", text: "A tool-calling agent that runs the tested calculators and cites guidelines — it never invents a score." },
  { icon: Database, title: "Quiver-powered RAG", text: "Guidelines and literature are retrieved from Quiver — a from-scratch vector database — for cited, in-context answers." },
  { icon: LineChart, title: "Analytics & monitoring", text: "Cohort distributions, risk mix and live post-op vitals, with real-time NEWS2 triage." },
];

const STACK = [
  "Next.js 15", "React 19", "TypeScript", "Tailwind", "FastAPI", "Python 3.12",
  "PostgreSQL 16", "Quiver", "LangGraph", "Groq", "Redis", "Docker",
];

function NavBar() {
  return (
    <header className="sticky top-0 z-40 border-b border-border/70 bg-background/80 backdrop-blur-md">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center">
          <PulseLogo />
        </Link>
        <nav className="hidden items-center gap-7 text-sm text-muted-foreground md:flex">
          <a href="#features" className="transition-colors hover:text-foreground">Features</a>
          <a href="#grounded" className="transition-colors hover:text-foreground">Grounded AI</a>
          <a href="#stack" className="transition-colors hover:text-foreground">Architecture</a>
        </nav>
        <div className="flex items-center gap-2">
          <ThemeToggle className="hidden sm:inline-flex" />
          <a href={GITHUB} target="_blank" rel="noreferrer" className="hidden sm:block">
            <Button variant="ghost" size="icon" aria-label="GitHub">
              <Github className="h-4 w-4" />
            </Button>
          </a>
          <Button asChild size="sm">
            <Link href="/login">
              Open the demo <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>
    </header>
  );
}

function DashboardMock() {
  return (
    <div className="rounded-xl border border-border bg-card shadow-lg">
      <div className="flex items-center gap-1.5 border-b border-border px-4 py-2.5">
        <span className="h-2.5 w-2.5 rounded-full bg-destructive/60" />
        <span className="h-2.5 w-2.5 rounded-full bg-warning/60" />
        <span className="h-2.5 w-2.5 rounded-full bg-success/60" />
        <span className="ml-2 font-mono text-[11px] text-muted-foreground">pulse — dashboard</span>
      </div>
      <div className="space-y-4 p-4">
        <div className="grid grid-cols-4 gap-3">
          {[
            { k: "Patients", v: "200", c: "text-foreground" },
            { k: "High NEWS2", v: "18", c: "text-destructive" },
            { k: "Borderline", v: "34", c: "text-warning" },
            { k: "Upcoming", v: "12", c: "text-success" },
          ].map((s) => (
            <div key={s.k} className="rounded-lg border border-border bg-background/60 p-2.5">
              <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{s.k}</p>
              <p className={`text-lg font-bold ${s.c}`}>{s.v}</p>
            </div>
          ))}
        </div>
        <div className="rounded-lg border border-border bg-background/60 p-3">
          <div className="mb-3 flex items-end gap-1.5">
            {[38, 52, 61, 74, 68, 83, 71, 56, 44, 30].map((h, i) => (
              <div key={i} className="flex-1 rounded-sm bg-primary/80" style={{ height: `${h}px` }} />
            ))}
          </div>
          <p className="text-[10px] text-muted-foreground">Aneurysm size distribution — 40–90mm</p>
        </div>
        <div className="flex items-center justify-between rounded-lg border border-border bg-background/60 p-2.5">
          <div className="flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/12 text-[10px] font-semibold text-primary">EV</span>
            <span className="text-xs text-foreground">EVAR · 68mm infrarenal AAA</span>
          </div>
          <Badge variant="warning">Borderline neck</Badge>
        </div>
      </div>
    </div>
  );
}

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <NavBar />

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-[0.4] [mask-image:radial-gradient(ellipse_at_top,black,transparent_70%)]" />
        <div className="container relative grid gap-12 py-20 lg:grid-cols-2 lg:items-center lg:py-28">
          <div className="space-y-6">
            <Badge variant="info" className="gap-1.5 px-3 py-1">
              <Sparkles className="h-3.5 w-3.5" /> Open-source · AI-native · Synthetic data
            </Badge>
            <h1 className="text-balance text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              Aortic surgery intelligence, from <span className="text-primary">referral to recovery</span>.
            </h1>
            <p className="max-w-xl text-lg text-muted-foreground">
              Pulse unifies the patient record, runs validated operative-risk scoring, matches stent-grafts on
              real IFU envelopes, and puts a grounded AI copilot on top — a decision-support workspace built to a
              production bar.
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <Button asChild size="lg">
                <Link href="/login">
                  Open the live demo <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <a href={GITHUB} target="_blank" rel="noreferrer">
                <Button variant="outline" size="lg">
                  <Github className="h-4 w-4" /> View source
                </Button>
              </a>
            </div>
            <p className="text-sm text-muted-foreground">
              Demo login <span className="font-mono text-foreground">surgeon@demo.pulse</span> ·{" "}
              <span className="font-mono text-foreground">demo-surgeon-2024</span>
            </p>
          </div>
          <div className="lg:pl-6">
            <DashboardMock />
          </div>
        </div>
      </section>

      {/* Workflow */}
      <section className="border-y border-border bg-muted/30">
        <div className="container py-16">
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {WORKFLOW.map((s) => (
              <div key={s.n} className="space-y-2.5">
                <div className="flex items-center gap-2.5">
                  <span className="font-mono text-sm text-primary">{s.n}</span>
                  <s.icon className="h-4 w-4 text-primary" />
                  <span className="text-sm font-semibold uppercase tracking-wide text-foreground">{s.label}</span>
                </div>
                <p className="text-sm text-muted-foreground">{s.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="container py-24">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Everything a case needs, in one workspace</h2>
          <p className="mt-4 text-muted-foreground">
            The clinical surface, the intelligence, and the data plane — designed together, not bolted on.
          </p>
        </div>
        <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="group rounded-xl border border-border bg-card p-6 transition-all hover:border-primary/40 hover:shadow-md"
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary transition-transform group-hover:scale-105">
                <f.icon className="h-5 w-5" />
              </div>
              <h3 className="font-semibold text-foreground">{f.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{f.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Grounded AI */}
      <section id="grounded" className="border-y border-border bg-muted/30">
        <div className="container grid gap-12 py-24 lg:grid-cols-2 lg:items-center">
          <div className="space-y-6">
            <Badge variant="info" className="gap-1.5"><BrainCircuit className="h-3.5 w-3.5" /> The copilot</Badge>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              AI that <span className="text-primary">never invents a number</span>
            </h2>
            <p className="text-muted-foreground">
              Ask the copilot for a patient’s operative risk and it doesn’t guess — it calls the same tested
              calculators the rest of the app uses, matches devices on their IFU envelopes, and retrieves the
              relevant guideline from Quiver. Every clinical claim is grounded in a tool result or a cited source,
              streamed step by step so you can see the reasoning.
            </p>
            <ul className="space-y-3 text-sm">
              {[
                "Tool-calling agent over the deterministic clinical engine",
                "Cited retrieval-augmented answers from the guideline base",
                "Streamed tool steps — RCRI, device-match, cohort query — in view",
              ].map((t) => (
                <li key={t} className="flex items-start gap-2.5 text-foreground">
                  <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-success" /> {t}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-xl border border-border bg-card p-5 shadow-lg">
            <div className="space-y-3 text-sm">
              <div className="ml-auto w-fit max-w-[85%] rounded-lg bg-primary px-3 py-2 text-primary-foreground">
                Is patient 42 suitable for EVAR, and what’s the RCRI?
              </div>
              <div className="space-y-2">
                <div className="flex flex-wrap gap-1.5">
                  <Badge variant="secondary" className="font-mono text-[10px]">▸ get_patient</Badge>
                  <Badge variant="secondary" className="font-mono text-[10px]">▸ calculate_risk_score: RCRI</Badge>
                  <Badge variant="secondary" className="font-mono text-[10px]">▸ match_devices</Badge>
                </div>
                <div className="max-w-[92%] rounded-lg bg-muted/60 px-3 py-2 text-foreground">
                  RCRI is <strong>2 (Class III, ~10.1%)</strong>. On anatomy, 3 of 4 grafts are IFU-suitable; the
                  neck angulation is borderline for one. Full report cites the ESVS 2024 AAA guideline.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Privacy */}
      <section className="container py-24">
        <div className="mx-auto flex max-w-3xl flex-col items-center gap-4 rounded-2xl border border-border bg-card p-10 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
            <Lock className="h-6 w-6" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight">100% synthetic. Zero PHI.</h2>
          <p className="max-w-xl text-muted-foreground">
            Every one of the ~200 patients is generated — clinically correlated, but entirely fictional. Pulse is
            an educational demonstration of a production-grade clinical tool, not a medical device, and carries its
            disclaimer on every clinical surface.
          </p>
        </div>
      </section>

      {/* Stack */}
      <section id="stack" className="border-t border-border bg-muted/30">
        <div className="container py-16 text-center">
          <p className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Built on</p>
          <div className="mx-auto mt-6 flex max-w-3xl flex-wrap justify-center gap-2.5">
            {STACK.map((t) => (
              <span key={t} className="rounded-full border border-border bg-background px-3.5 py-1.5 text-sm text-foreground">
                {t}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container py-24">
        <div className="relative overflow-hidden rounded-2xl bg-primary px-8 py-16 text-center text-primary-foreground">
          <div className="absolute inset-0 bg-grid opacity-10" />
          <div className="relative mx-auto max-w-xl space-y-5">
            <h2 className="text-3xl font-bold tracking-tight">See the whole case in one place</h2>
            <p className="text-primary-foreground/80">
              Sign in with the demo account and browse 200 synthetic patients, run the calculators, and ask the copilot.
            </p>
            <Button asChild size="lg" variant="secondary">
              <Link href="/login">
                Open the live demo <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border">
        <div className="container flex flex-col items-center justify-between gap-4 py-8 sm:flex-row">
          <PulseLogo className="h-6" />
          <p className="text-center text-xs text-muted-foreground">
            Educational demo on synthetic data — not for clinical use; not medical advice.
          </p>
          <a href={GITHUB} target="_blank" rel="noreferrer" className="text-muted-foreground transition-colors hover:text-foreground">
            <Github className="h-5 w-5" />
          </a>
        </div>
      </footer>
    </div>
  );
}
