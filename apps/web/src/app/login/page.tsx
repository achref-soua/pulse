"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, ArrowRight, ShieldCheck, Sparkles, Stethoscope } from "lucide-react";
import { Button, Input, Label } from "@pulse/ui";
import { api } from "@/lib/api";
import { PulseLogo } from "@/components/brand/PulseLogo";

const HIGHLIGHTS = [
  { icon: Sparkles, text: "Grounded AI copilot that calls tested calculators — never invents a score" },
  { icon: ShieldCheck, text: "7 validated risk models: RCRI, EuroSCORE II, CHA₂DS₂-VASc, NEWS2 & more" },
  { icon: Stethoscope, text: "Anatomical IFU device-fit matching across a stent-graft catalogue" },
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await api.post<{ access_token: string; refresh_token: string }>("/auth/login", {
        email,
        password,
      });
      localStorage.setItem("pulse_access_token", data.access_token);
      localStorage.setItem("pulse_refresh_token", data.refresh_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* Brand panel */}
      <div className="relative hidden overflow-hidden bg-primary p-12 text-primary-foreground lg:flex lg:flex-col lg:justify-between">
        <div className="absolute inset-0 bg-grid opacity-[0.12]" />
        <div
          className="absolute -right-24 -top-24 h-96 w-96 rounded-full opacity-30 blur-3xl"
          style={{ background: "radial-gradient(circle, hsl(0 0% 100% / 0.35), transparent 70%)" }}
        />
        <div className="relative flex items-center gap-2">
          <PulseLogo className="h-8 text-primary-foreground" />
        </div>

        <div className="relative space-y-8">
          <div className="space-y-3">
            <p className="inline-flex items-center gap-1.5 rounded-full border border-primary-foreground/20 bg-primary-foreground/10 px-3 py-1 text-xs font-medium">
              <Activity className="h-3.5 w-3.5" /> Aortic &amp; endovascular intelligence
            </p>
            <h1 className="text-balance text-4xl font-bold leading-tight tracking-tight">
              From referral to recovery, one clinical picture.
            </h1>
            <p className="max-w-md text-primary-foreground/80">
              Pulse unifies patient anatomy, validated risk scoring, device suitability and a
              grounded AI copilot into a single decision-support workspace.
            </p>
          </div>
          <ul className="space-y-3">
            {HIGHLIGHTS.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-start gap-3 text-sm text-primary-foreground/90">
                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-primary-foreground/15">
                  <Icon className="h-3.5 w-3.5" />
                </span>
                {text}
              </li>
            ))}
          </ul>
        </div>

        <p className="relative text-xs text-primary-foreground/70">
          Educational demonstration on fully synthetic patient data — not for clinical use.
        </p>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm space-y-8">
          <div className="space-y-2 lg:hidden">
            <PulseLogo className="h-8" />
          </div>
          <div className="space-y-1.5">
            <h2 className="text-2xl font-semibold tracking-tight">Sign in</h2>
            <p className="text-sm text-muted-foreground">Welcome back — access your workspace.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="surgeon@demo.pulse"
                autoComplete="email"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </div>

            {error && (
              <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </p>
            )}

            <Button type="submit" size="lg" disabled={loading} className="w-full">
              {loading ? "Signing in…" : "Sign in"}
              {!loading && <ArrowRight className="h-4 w-4" />}
            </Button>
          </form>

          <div className="rounded-lg border border-border bg-muted/40 p-3.5">
            <p className="mb-1.5 text-xs font-semibold text-foreground">Demo credentials</p>
            <div className="space-y-0.5 font-mono text-xs text-muted-foreground">
              <p>surgeon@demo.pulse / demo-surgeon-2024</p>
              <p>nurse@demo.pulse / demo-nurse-2024</p>
              <p>admin@demo.pulse / demo-admin-2024</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
