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
const OUT_DIR = path.resolve(__dirname, "../../../docs/assets");

const SURGEON_EMAIL = process.env.SURGEON_EMAIL ?? "surgeon@pulse.test";
const SURGEON_PASSWORD = process.env.SURGEON_PASSWORD ?? "PulseDemo1!";
const ADMIN_EMAIL = process.env.ADMIN_EMAIL ?? "admin@pulse.test";
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD ?? "PulseDemo1!";

fs.mkdirSync(OUT_DIR, { recursive: true });

async function shot(page: Page, name: string, fullPage = false) {
  const dest = path.join(OUT_DIR, `${name}.png`);
  await page.screenshot({ path: dest, fullPage });
  console.log(`  ✓ ${name}.png`);
}

async function loginAs(page: Page, email: string, password: string) {
  await page.goto(`${BASE_URL}/login`);
  await page.fill('[name="email"]', email);
  await page.fill('[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/(dashboard|patients)/, { timeout: 12000 });
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

/** Return hrefs for up to `max` patient rows. */
async function collectPatientIds(page: Page, max = 4): Promise<string[]> {
  await page.goto(`${BASE_URL}/patients`);
  await idle(page, 800);
  const rows = page.locator("tbody tr");
  const count = Math.min(await rows.count(), max);
  const ids: string[] = [];
  for (let i = 0; i < count; i++) {
    const href = await rows.nth(i).locator("a, [data-href]").first().getAttribute("href").catch(() => null);
    if (href) ids.push(href);
  }
  return ids;
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

    // 2. Dashboard
    await page.goto(`${BASE_URL}/dashboard`);
    await idle(page, 800);
    await shot(page, "dashboard");

    // 3. Patients list
    await page.goto(`${BASE_URL}/patients`);
    await idle(page, 800);
    await shot(page, "patients-list");

    // 4–N. First 3 patients — capture Overview + all tabs
    const patientLinks = await collectPatientIds(page, 3);

    for (let pi = 0; pi < patientLinks.length; pi++) {
      const href = patientLinks[pi];
      const tag = `patient${pi + 1}`;

      // Overview tab
      await page.goto(`${BASE_URL}${href}`);
      await idle(page, 800);
      await shot(page, `${tag}-overview`);

      // Anatomy tab
      if (await clickTab(page, /anatomy/i)) await shot(page, `${tag}-anatomy`);

      // Risk & Suitability tab
      if (await clickTab(page, /risk/i)) await shot(page, `${tag}-risk`);

      // Monitoring tab
      if (await clickTab(page, /monitoring/i)) await shot(page, `${tag}-monitoring`);

      // Post-op tab (only present for post-op phase patients)
      if (await clickTab(page, /post.?op/i)) await shot(page, `${tag}-postop`);

      // AI Summary tab
      if (await clickTab(page, /ai.?summ|copilot/i)) await shot(page, `${tag}-ai-summary`);
    }

    // 5. Risk calculators — landing page
    await page.goto(`${BASE_URL}/risk`);
    await idle(page, 600);
    await shot(page, "risk-calculators");

    // RCRI calculator
    const rcriBtn = page.locator("button").filter({ hasText: /RCRI/i }).first();
    if (await rcriBtn.isVisible({ timeout: 4000 }).catch(() => false)) {
      await rcriBtn.click();
      await idle(page, 400);
      await shot(page, "risk-rcri-form");
      // Fill a couple of checkboxes and calculate
      const boxes = page.locator('input[type="checkbox"]');
      const boxCount = await boxes.count();
      if (boxCount >= 2) {
        await boxes.nth(0).check().catch(() => {});
        await boxes.nth(1).check().catch(() => {});
      }
      await page.locator('button:has-text("Calculate"), button[type="submit"]').first().click().catch(() => {});
      await idle(page, 400);
      await shot(page, "risk-rcri-result");
    }

    // NEWS2 calculator
    const news2Btn = page.locator("button").filter({ hasText: /NEWS2/i }).first();
    if (await news2Btn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await news2Btn.click();
      await idle(page, 400);
      await shot(page, "risk-news2-form");
      await page.locator('button:has-text("Calculate"), button[type="submit"]').first().click().catch(() => {});
      await idle(page, 400);
      await shot(page, "risk-news2-result");
    }

    // GAS calculator
    const gasBtn = page.locator("button").filter({ hasText: /GAS|Global/i }).first();
    if (await gasBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await gasBtn.click();
      await idle(page, 400);
      await shot(page, "risk-gas-form");
      await page.locator('button:has-text("Calculate"), button[type="submit"]').first().click().catch(() => {});
      await idle(page, 400);
      await shot(page, "risk-gas-result");
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
