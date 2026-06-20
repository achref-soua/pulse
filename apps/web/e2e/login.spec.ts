import { test, expect } from "@playwright/test";

test.describe("login flow", () => {
  test("shows login form", async ({ page }) => {
    await page.goto("/login");
    await expect(page.locator('[name="email"]')).toBeVisible();
    await expect(page.locator('[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test("rejects invalid credentials", async ({ page }) => {
    await page.goto("/login");
    await page.fill('[name="email"]', "nobody@example.com");
    await page.fill('[name="password"]', "wrongpassword");
    await page.click('button[type="submit"]');
    // Should stay on /login and show an error
    await expect(page).toHaveURL(/\/login/);
    await expect(page.locator("text=Incorrect email or password")).toBeVisible({
      timeout: 5000,
    });
  });

  test("redirects unauthenticated user away from dashboard", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/);
  });

  test("surgeon login → redirects to dashboard", async ({ page }) => {
    await page.goto("/login");
    await page.fill('[name="email"]', "surgeon@pulse.test");
    await page.fill('[name="password"]', "PulseDemo1!");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/(dashboard|patients)/, { timeout: 8000 });
  });
});
