import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers";

test.describe("risk calculator", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, "surgeon");
    await page.goto("/risk");
    await page.waitForSelector("h1", { timeout: 8000 });
  });

  test("renders calculator picker", async ({ page }) => {
    await expect(page.locator("h1")).toContainText("Risk");
    // RCRI button should be visible
    await expect(page.locator("button, [role='button']").filter({ hasText: /RCRI/i })).toBeVisible();
  });

  test("RCRI form appears after selecting RCRI", async ({ page }) => {
    await page.click("button:has-text('RCRI'), [data-calc='rcri']");
    // Form checkboxes should appear
    await expect(page.locator('input[type="checkbox"]').first()).toBeVisible({ timeout: 5000 });
  });

  test("RCRI form submits and shows result panel", async ({ page }) => {
    // Select RCRI
    const rcriBtn = page.locator("button").filter({ hasText: /RCRI/ }).first();
    await rcriBtn.click();

    // Wait for form
    await page.waitForSelector('input[type="checkbox"]', { timeout: 5000 });

    // Submit
    await page.click('button[type="submit"], button:has-text("Calculate")');

    // Result panel should appear
    await expect(page.locator("text=Result")).toBeVisible({ timeout: 8000 });
  });

  test("NEWS2 calculator is selectable", async ({ page }) => {
    const news2Btn = page.locator("button").filter({ hasText: /NEWS2/ }).first();
    await news2Btn.click();
    await expect(page.locator('input[type="number"]').first()).toBeVisible({ timeout: 5000 });
  });
});
