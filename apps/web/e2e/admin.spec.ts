import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers";

test.describe("admin access control", () => {
  test("surgeon is redirected away from /admin", async ({ page }) => {
    await loginAs(page, "surgeon");
    await page.goto("/admin");
    // Should redirect to dashboard or show access-denied
    await expect(page).not.toHaveURL(/\/admin/, { timeout: 5000 });
  });

  test("admin can access /admin and sees users tab", async ({ page }) => {
    await loginAs(page, "admin");
    await page.goto("/admin");
    await expect(page.locator("h1")).toContainText("Admin", { timeout: 8000 });
    await expect(page.locator("button, [role='tab']").filter({ hasText: /Users/i })).toBeVisible();
  });

  test("admin audit log tab loads", async ({ page }) => {
    await loginAs(page, "admin");
    await page.goto("/admin");
    await page.click("button:has-text('Audit Log')");
    await expect(
      page.locator("table, text=No audit entries")
    ).toBeVisible({ timeout: 8000 });
  });
});
