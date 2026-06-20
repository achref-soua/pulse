"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

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
      const data = await api.post<{ access_token: string; refresh_token: string }>(
        "/auth/login",
        { email, password }
      );
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
    <div className="min-h-screen flex items-center justify-center bg-background pb-12">
      <div className="w-full max-w-sm space-y-6 rounded-xl border border-border bg-card p-8 shadow-xl">
        {/* Logo */}
        <div className="flex flex-col items-center gap-2">
          <svg width="60" height="30" viewBox="0 0 80 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polyline
              points="0,20 15,20 22,5 30,35 38,10 46,30 54,20 80,20"
              stroke="#E11D48"
              strokeWidth="2.5"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <h1 className="text-xl font-bold tracking-tight">Pulse</h1>
          <p className="text-xs text-muted-foreground text-center">
            Aortic &amp; endovascular surgery intelligence
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="surgeon@demo.pulse"
            />
          </div>
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div className="rounded-md border border-border/50 bg-muted/30 p-3">
          <p className="text-xs text-muted-foreground font-medium mb-1">Demo credentials</p>
          <p className="text-xs text-muted-foreground">surgeon@demo.pulse / demo-surgeon-2024</p>
          <p className="text-xs text-muted-foreground">nurse@demo.pulse / demo-nurse-2024</p>
          <p className="text-xs text-muted-foreground">admin@demo.pulse / demo-admin-2024</p>
        </div>
      </div>
    </div>
  );
}
