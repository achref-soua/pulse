#!/usr/bin/env node
/**
 * Screenshot capture script — saves docs/assets/*.png
 * Covers multiple patients, all tabs, multiple calculators, admin views.
 *
 * Usage:
 *   BASE_URL=http://localhost:3000 npx tsx scripts/screenshots.ts
 *
 * Credentials (env or demo defaults):
 *   SURGEON_EMAIL  SURGEON_PASSWORD  ADMIN_EMAIL  ADMIN_PASSWORD
 */
import { chromium, Browser, Page } from "@playwright/test";
import path from "path";
import fs from "fs";

const BASE_URL = process.env.BASE_URL ?? "http://localhost:3000";
const API_URL = process.env.API_URL ?? "http://localhost:8000";
const OUT_DIR = path.resolve(__dirname, "../../../docs/assets");

const SURGEON_EMAIL = process.env.SURGEON_EMAIL ?? "surgeon@demo.pulse";
const SURGEON_PASSWORD = process.env.SURGEON_PASSWORD ?? "demo-surgeon-2024";
const ADMIN_EMAIL = process.env.ADMIN_EMAIL ?? "admin@demo.pulse";
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD ?? "demo-admin-2024";

fs.mkdirSync(OUT_DIR, { recursive: true });

async function shot(page: Page, name: string, fullPage = false) {
  const dest = path.join(OUT_DIR, `${name}.png`);
  await page.screenshot({ path: dest, fullPage });
  console.log(`  ✓ ${name}.png`);
}

/** Get tokens from API via Node fetch (bypasses browser CORS), inject into localStorage. */
async function loginAs(page: Page, email: string, password: string) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(`Login failed for ${email}: ${res.status}`);
  const { access_token, refresh_token } = (await res.json()) as {
    access_token: string;
    refresh_token: string;
  };

  // Load any page first so we have a context to set localStorage on
  await page.goto(`${BASE_URL}/login`);
  await page.waitForLoadState("domcontentloaded");
  await page.evaluate(
    ({ at, rt }) => {
      localStorage.setItem("pulse_access_token", at);
      localStorage.setItem("pulse_refresh_token", rt);
    },
    { at: access_token, rt: refresh_token }
  );
  await page.goto(`${BASE_URL}/dashboard`);
  await page.waitForURL(/\/dashboard/, { timeout: 15000 });
}

async function idle(page: Page, ms = 600) {
  await page.waitForTimeout(ms);
  await page.waitForLoadState("networkidle", { timeout: 10000 }).catch(() => {});
}

async function clickTab(page: Page, label: RegExp | string): Promise<boolean> {
  const tab = page.locator("button, [role='tab']").filter({ hasText: label }).first();
  if (await tab.isVisible({ timeout: 3000 }).catch(() => false)) {
    await tab.click();
    await idle(page);
    return true;
  }
  return false;
}

/** Return patient_id slugs from the API (avoids scraping the table). */
async function fetchPatientSlugs(count = 3): Promise<string[]> {
  const token = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: SURGEON_EMAIL, password: SURGEON_PASSWORD }),
  }).then((r) => r.json()).then((d) => d.access_token as string);

  const patients = await fetch(`${API_URL}/patients?limit=${count}`, {
    headers: { Authorization: `Bearer ${token}` },
  }).then((r) => r.json()) as Array<{ patient_id: string }>;

  return patients.map((p) => p.patient_id);
}

async function run() {
  let browser: Browser | undefined;
  try {
    browser = await chromium.launch({ headless: true });

    // ─────────────────────────────────────────────────────────────────────────
    // Surgeon session
    // ─────────────────────────────────────────────────────────────────────────
    console.log("\nSurgeon session");
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await ctx.newPage();
    await loginAs(page, SURGEON_EMAIL, SURGEON_PASSWORD);

    // 1. Login screen (before auth)
    const anonCtx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const anonPage = await anonCtx.newPage();
    await anonPage.goto(`${BASE_URL}/login`);
    await idle(anonPage, 400);
    await shot(anonPage, "login");
    await anonCtx.close();

    // 2. Dashboard — wait for stat cards to hydrate
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
    await idle(page, 1500);
    await shot(page, "dashboard");

    // 3. Patients list
    await page.goto(`${BASE_URL}/patients`);
    await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});
    await idle(page, 1000);
    await shot(page, "patients-list");

    // 4–N. First 3 patients — capture Overview + all tabs
    const slugs = await fetchPatientSlugs(3);

    for (let pi = 0; pi < slugs.length; pi++) {
      const slug = slugs[pi];
      const tag = `patient${pi + 1}`;

      // Overview (default tab) — wait for patient data to load from API
      await page.goto(`${BASE_URL}/patients/${slug}`);
      await page.waitForLoadState("networkidle", { timeout: 20000 }).catch(() => {});
      await idle(page, 1200);
      await shot(page, `${tag}-overview`);

      // Patient detail tabs — these labels are unique to the tab bar, not the sidebar
      for (const [label, suffix] of [
        ["Risk & Suitability", "risk"],
        ["Notes", "notes"],
        ["Post-op", "postop"],
        ["AI Summary", "ai-summary"],
      ] as [string, string][]) {
        const btn = page.getByRole("button", { name: label, exact: true }).first();
        const visible = await btn.isVisible({ timeout: 4000 }).catch(() => false);
        if (visible) {
          await btn.click();
          await idle(page, 800);
          await shot(page, `${tag}-${suffix}`);
        }
      }
    }

    // 5. Risk calculators — navigate once, click each selector tab
    await page.goto(`${BASE_URL}/risk`);
    await page.waitForSelector("button", { timeout: 10000 });
    await idle(page, 800);
    await shot(page, "risk-calculators");

    for (const [calcLabel, calcId] of [
      ["RCRI", "rcri"],
      ["NEWS2", "news2"],
      ["GAS", "gas"],
    ] as [string, string][]) {
      // Click the small selector button (exact text label, not "Calculate X")
      await page.locator(`button:text-is("${calcLabel}")`).first().click().catch(() => {});
      await idle(page, 500);
      await shot(page, `risk-${calcId}-form`);

      // Tick up to 2 checkboxes
      const boxes = page.locator('input[type="checkbox"]');
      const n = await boxes.count();
      for (let i = 0; i < Math.min(n, 2); i++) await boxes.nth(i).check().catch(() => {});

      // Submit
      await page.locator(`button:has-text("Calculate")`).last().click().catch(() => {});
      await idle(page, 700);
      await shot(page, `risk-${calcId}-result`);
    }

    // 6. Devices
    await page.goto(`${BASE_URL}/devices`);
    await idle(page, 800);
    await shot(page, "devices");

    // Open first device detail/modal
    const devRow = page.locator("tbody tr, [data-testid='device-card']").first();
    if (await devRow.isVisible({ timeout: 4000 }).catch(() => false)) {
      await devRow.click();
      await idle(page, 500);
      await shot(page, "devices-detail");
      await page.keyboard.press("Escape");
    }

    // 7. Monitoring — multiple patients
    await page.goto(`${BASE_URL}/monitoring`);
    await idle(page, 800);
    await shot(page, "monitoring");

    // Filter to a different patient if selector exists
    const monSelect = page.locator("select").first();
    if (await monSelect.isVisible({ timeout: 3000 }).catch(() => false)) {
      const opts = await monSelect.locator("option").all();
      if (opts.length > 2) {
        await monSelect.selectOption({ index: 2 });
        await idle(page, 600);
        await shot(page, "monitoring-patient2");
      }
    }

    // 8. Knowledge Base
    await page.goto(`${BASE_URL}/knowledge`);
    await idle(page, 700);
    await shot(page, "knowledge-base");

    // 9. AI Copilot panel open
    await page.goto(`${BASE_URL}/dashboard`);
    await idle(page, 600);
    const copilotBtn = page.locator("button").filter({ hasText: /AI Copilot|Copilot/i }).first();
    if (await copilotBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await copilotBtn.click();
      await idle(page, 500);
      await shot(page, "ai-copilot-panel");
    }

    // 10. Settings
    await page.goto(`${BASE_URL}/settings`);
    await idle(page, 500);
    await shot(page, "settings");

    await ctx.close();

    // ─────────────────────────────────────────────────────────────────────────
    // Admin session
    // ─────────────────────────────────────────────────────────────────────────
    console.log("\nAdmin session");
    const adminCtx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const adminPage = await adminCtx.newPage();
    await loginAs(adminPage, ADMIN_EMAIL, ADMIN_PASSWORD);

    await adminPage.goto(`${BASE_URL}/admin`);
    await idle(adminPage, 700);
    await shot(adminPage, "admin-users");

    // Audit log tab
    if (await clickTab(adminPage, /audit/i)) {
      await shot(adminPage, "admin-audit-log");
    }

    // Full-page scroll of users list
    await adminPage.goto(`${BASE_URL}/admin`);
    await idle(adminPage, 600);
    await shot(adminPage, "admin-users-full", true);

    await adminCtx.close();

    console.log(`\nAll screenshots saved → ${OUT_DIR}\n`);
  } finally {
    await browser?.close();
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
