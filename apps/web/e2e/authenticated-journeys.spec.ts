import { expect, test, type Page } from "@playwright/test";

type TestIdentity = {
  username: string;
  password: string;
};

function requiredIdentity(prefix: "ADMIN" | "ANALYST" | "VIEWER"): TestIdentity {
  const username = process.env[`AUTOSOC_E2E_${prefix}_USERNAME`];
  const password = process.env[`AUTOSOC_E2E_${prefix}_PASSWORD`];
  if (!username || !password) {
    throw new Error(`Missing protected AUTOSOC_E2E_${prefix}_USERNAME/PASSWORD test environment values.`);
  }
  return { username, password };
}

async function signInWithKeycloak(page: Page, identity: TestIdentity) {
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: "Sign in to AutoSOC" })).toBeVisible();
  await page.getByRole("button", { name: "Sign in with AutoSOC Identity" }).click();
  await expect(page).toHaveURL(/\/realms\/autosoc\/protocol\/openid-connect\/auth/);
  await page.locator("#username").fill(identity.username);
  await page.locator("#password").fill(identity.password);
  await page.locator("#kc-login").click();
  await expect(page).toHaveURL(/\/dashboard$/, { timeout: 30_000 });
  await expect(page.getByRole("heading", { name: "Security operations" })).toBeVisible({ timeout: 15_000 });
}

async function signOut(page: Page) {
  await page.getByRole("button", { name: "Open account menu" }).last().click();
  await page.getByRole("menuitem", { name: "Sign out" }).click();
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "Sign in to AutoSOC" })).toBeVisible();
}

test.describe("administrator OIDC journey", () => {
  test("loads persisted security views, supports event pagination, and logs out", async ({ page }) => {
    await signInWithKeycloak(page, requiredIdentity("ADMIN"));

    for (const route of [
      ["/events", "Log explorer"],
      ["/alerts", "Alert triage"],
      ["/incidents", "Incident workspace"],
      ["/agents", "AI investigation center"],
      ["/responses", "Response management"],
      ["/audit", "Audit activity"],
      ["/system-health", "System health"],
    ] as const) {
      await page.goto(route[0]);
      await expect(page.getByRole("heading", { name: route[1], exact: true })).toBeVisible();
    }

    await page.goto("/events");
    const eventSearch = page.locator("#event-search");
    await eventSearch.fill("powershell");
    await page.getByRole("button", { name: "Query" }).click();
    await expect(page.getByText(/matching events|No security events found/i)).toBeVisible();
    const next = page.getByRole("button", { name: "Next", exact: true });
    if (await next.isEnabled()) {
      await next.click();
      await expect(page.getByRole("heading", { name: "Log explorer" })).toBeVisible();
    }

    await page.goto("/responses");
    await expect(page.getByText("Validated only — no external action performed.")).toBeVisible();
    await signOut(page);
  });
});

test.describe("analyst OIDC journey", () => {
  test("can investigate permitted records but does not receive administrator review controls", async ({ page }) => {
    await signInWithKeycloak(page, requiredIdentity("ANALYST"));
    await page.goto("/incidents");
    await expect(page.getByRole("heading", { name: "Incident workspace" })).toBeVisible();
    await page.goto("/responses");
    await expect(page.getByRole("heading", { name: "Response management" })).toBeVisible();
    const approvedButton = page.getByRole("button", { name: "Approve" });
    await expect(approvedButton).toHaveCount(0);
    await signOut(page);
  });
});

test.describe("viewer OIDC journey", () => {
  test("can read permitted views while mutation controls remain unavailable", async ({ page }) => {
    await signInWithKeycloak(page, requiredIdentity("VIEWER"));
    await page.goto("/events");
    await expect(page.getByRole("heading", { name: "Log explorer" })).toBeVisible();
    await page.goto("/responses");
    await expect(page.getByRole("heading", { name: "Response management" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Audit Activity" })).toHaveCount(0);
    await signOut(page);
  });
});

test.describe("responsive and keyboard checks", () => {
  for (const [label, width, height] of [
    ["mobile", 375, 812],
    ["tablet", 768, 1024],
    ["laptop", 1280, 900],
    ["desktop", 1920, 1080],
  ] as const) {
    test(`${label} dashboard avoids horizontal document overflow`, async ({ page }) => {
      await page.setViewportSize({ width, height });
      await signInWithKeycloak(page, requiredIdentity("VIEWER"));
      if (width < 768) {
        await page.getByRole("button", { name: "Open navigation menu" }).click();
        await expect(page.getByRole("dialog", { name: "Navigation menu" })).toBeVisible();
        await page.keyboard.press("Escape");
      }
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
      expect(overflow).toBeFalsy();
      await page.keyboard.press("Tab");
      await expect(page.locator(":focus")).toBeVisible();
      await signOut(page);
    });
  }
});
