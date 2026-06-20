import { Page } from "@playwright/test";

export const TEST_CREDS = {
  surgeon: { email: "surgeon@pulse.test", password: "PulseDemo1!" },
  admin: { email: "admin@pulse.test", password: "PulseDemo1!" },
};

export async function loginAs(page: Page, role: "surgeon" | "admin") {
  const creds = TEST_CREDS[role];
  await page.goto("/login");
  await page.fill('[name="email"]', creds.email);
  await page.fill('[name="password"]', creds.password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/(dashboard|patients)/);
}
