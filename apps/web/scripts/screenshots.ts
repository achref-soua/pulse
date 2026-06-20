#!/usr/bin/env node
/**
 * Screenshot capture script — saves docs/assets/*.png
 * Run via: task screenshots (requires a running stack on BASE_URL)
 *
 * Usage:
 *   BASE_URL=http://localhost:3000 npx tsx scripts/screenshots.ts
 *
 * Credentials are read from environment:
 *   SURGEON_EMAIL   SURGEON_PASSWORD
 *   ADMIN_EMAIL     ADMIN_PASSWORD
 */
import { chromium, Browser, Page } from "@playwright/test";
import path from "path";
import fs from "fs";

const BASE_URL = process.env.BASE_URL ?? "http://localhost:3000";
const OUT_DIR = path.resolve(__dirname, "../../../docs/assets");

const SURGEON_EMAIL = process.env.SURGEON_EMAIL ?? "surgeon@pulse.test";
const SURGEON_PASSWORD = process.env.SURGEON_PASSWORD ?? "PulseDemo1!";
const ADMIN_EMAIL = process.env.ADMIN_EMAIL ?? "admin@pulse.test";
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD ?? "PulseDemo1!";

fs.mkdirSync(OUT_DIR, { recursive: true });

async function shot(page: Page, name: string) {
  const dest = path.join(OUT_DIR, `${name}.png`);
  await page.screenshot({ path: dest, fullPage: false });
  console.log(`  ✓ ${name}.png`);
}

async function loginAs(page: Page, email: string, password: string) {
  await page.goto(`${BASE_URL}/login`);
  await page.fill('[name="email"]', email);
  await page.fill('[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/(dashboard|patients)/, { timeout: 10000 });
}

async function waitReady(page: Page) {
  await page.waitForLoadState("networkidle", { timeout: 12000 }).catch(() => {
    // networkidle can be flaky with polling — continue anyway
  });
}

async function run() {
  let browser: Browser | undefined;
  try {
    browser = await chromium.launch({ headless: true });
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await ctx.newPage();

    // ── Surgeon session ──────────────────────────────────────────────
    console.log("\nSurgeon session");
    await loginAs(page, SURGEON_EMAIL, SURGEON_PASSWORD);

    // Dashboard
    await page.goto(`${BASE_URL}/dashboard`);
    await waitReady(page);
    await shot(page, "dashboard");

    // Patients list
    await page.goto(`${BASE_URL}/patients`);
    await waitReady(page);
    await shot(page, "patients-list");

    // Patient detail — grab first patient id from the table
    const firstRow = page.locator("tbody tr").first();
    await firstRow.waitFor({ timeout: 8000 }).catch(() => {});
    await firstRow.click().catch(() => {});
    await waitReady(page);
    await shot(page, "patient-overview");

    // Risk & Suitability tab
    const riskTab = page.locator("button").filter({ hasText: /Risk/i }).first();
    await riskTab.click().catch(() => {});
    await waitReady(page);
    await shot(page, "patient-risk-tab");

    // Post-op tab (may not be visible for all patients)
    const postOpTab = page.locator("button").filter({ hasText: /Post.op/i }).first();
    if (await postOpTab.isVisible().catch(() => false)) {
      await postOpTab.click();
      await waitReady(page);
      await shot(page, "patient-postop-tab");
    }

    // Risk calculators
    await page.goto(`${BASE_URL}/risk`);
    await waitReady(page);
    await shot(page, "risk-calculators");

    // RCRI result
    const rcriBtn = page.locator("button").filter({ hasText: /RCRI/ }).first();
    await rcriBtn.click().catch(() => {});
    await page.waitForSelector('input[type="checkbox"]', { timeout: 5000 }).catch(() => {});
    await page.click('button[type="submit"], button:has-text("Calculate")').catch(() => {});
    await waitReady(page);
    await shot(page, "risk-rcri-result");

    // Devices
    await page.goto(`${BASE_URL}/devices`);
    await waitReady(page);
    await shot(page, "devices");

    // Monitoring
    await page.goto(`${BASE_URL}/monitoring`);
    await waitReady(page);
    await shot(page, "monitoring");

    // Settings
    await page.goto(`${BASE_URL}/settings`);
    await waitReady(page);
    await shot(page, "settings");

    await ctx.close();

    // ── Admin session ────────────────────────────────────────────────
    console.log("\nAdmin session");
    const adminCtx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const adminPage = await adminCtx.newPage();

    await loginAs(adminPage, ADMIN_EMAIL, ADMIN_PASSWORD);
    await adminPage.goto(`${BASE_URL}/admin`);
    await waitReady(adminPage);
    await shot(adminPage, "admin-users");

    await adminPage.click("button:has-text('Audit Log')").catch(() => {});
    await waitReady(adminPage);
    await shot(adminPage, "admin-audit-log");

    await adminCtx.close();

    console.log(`\nAll screenshots saved to ${OUT_DIR}\n`);
  } finally {
    await browser?.close();
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
