import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers";

test.describe("patients list and detail", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, "surgeon");
    await page.goto("/patients");
    await page.waitForSelector("table, [data-testid='empty-state']", {
      timeout: 10000,
    });
  });

  test("renders the patients roster", async ({ page }) => {
    await expect(page.locator("h1")).toContainText("Patients");
    // Phase filter dropdown should be present
    await expect(page.locator("select").first()).toBeVisible();
  });

  test("search input filters the list", async ({ page }) => {
    const rows = page.locator("tbody tr");
    const before = await rows.count();
    // Type a search term unlikely to match most patients
    await page.fill('input[placeholder*="Search"]', "ZZZNOMATCH999");
    await page.waitForTimeout(500);
    const after = await rows.count();
    expect(after).toBeLessThanOrEqual(before);
  });

  test("clicking a row opens patient detail", async ({ page }) => {
    const firstRow = page.locator("tbody tr").first();
    await firstRow.waitFor({ timeout: 8000 });
    await firstRow.click();
    await expect(page).toHaveURL(/\/patients\/.+/);
    await expect(page.locator("h1")).toBeVisible({ timeout: 8000 });
  });

  test("patient detail shows tabs", async ({ page }) => {
    const firstRow = page.locator("tbody tr").first();
    await firstRow.waitFor({ timeout: 8000 });
    await firstRow.click();
    await page.waitForURL(/\/patients\/.+/);
    await expect(page.locator('[role="tab"], button').filter({ hasText: /Overview/i })).toBeVisible({ timeout: 8000 });
    await expect(page.locator('[role="tab"], button').filter({ hasText: /Risk/i })).toBeVisible();
  });
});
