import { expect, test, type Browser, type Page } from "@playwright/test";

const applicationUrl = "http://127.0.0.1:3000";
const verificationApi = process.env.AUTOSOC_E2E_VERIFY_API ?? "http://127.0.0.1:8004/api/v1";
const ingestionApi = "http://127.0.0.1:8001/api/v1/ingest/events";

function adminIdentity() {
  const username = process.env.AUTOSOC_E2E_ADMIN_USERNAME;
  const password = process.env.AUTOSOC_E2E_ADMIN_PASSWORD;
  if (!username || !password) throw new Error("Missing protected administrator browser-test credentials.");
  return { username, password };
}

async function signedInPage(browser: Browser): Promise<Page> {
  const page = await browser.newPage();
  const identity = adminIdentity();
  await page.goto(`${applicationUrl}/login`);
  await page.getByRole("button", { name: "Sign in with AutoSOC Identity" }).click();
  await page.locator("#username").fill(identity.username);
  await page.locator("#password").fill(identity.password);
  await page.locator("#kc-login").click();
  await expect(page).toHaveURL(/\/dashboard$/, { timeout: 30_000 });
  return page;
}

async function accessToken(page: Page): Promise<string> {
  const value = await page.evaluate(async () => {
    const response = await fetch("/api/auth/session");
    const session: unknown = await response.json();
    return session && typeof session === "object" && "accessToken" in session && typeof session.accessToken === "string"
      ? session.accessToken
      : null;
  });
  if (!value) throw new Error("No browser access token was available.");
  return value;
}

test("administrator provisions a one-time source key and revokes ingestion access", async ({ browser }) => {
  const page = await signedInPage(browser);
  const token = await accessToken(page);
  const sourceName = `phase6-security-${Date.now()}`;
  const headers = { Authorization: `Bearer ${token}` };

  const created = await page.request.post(`${verificationApi}/data-sources`, {
    headers,
    data: {
      name: sourceName,
      source_type: "synthetic",
      environment: "development",
      description: "Ephemeral Phase 6 source-key security verification.",
      enabled: true,
    },
  });
  expect(created.status()).toBe(200);
  const source = await created.json() as { id: string; api_key?: string };
  expect(source.api_key).toMatch(/^asoc_[A-Za-z0-9_-]{40,}$/);

  const listed = await page.request.get(`${verificationApi}/data-sources`, { headers });
  expect(listed.status()).toBe(200);
  const listBody = await listed.json() as { items: Array<Record<string, unknown>> };
  const listedSource = listBody.items.find((candidate) => candidate.id === source.id);
  expect(listedSource).toBeTruthy();
  expect(listedSource).not.toHaveProperty("api_key");
  expect(listedSource).not.toHaveProperty("api_key_hash");

  const revoked = await page.request.post(`${verificationApi}/data-sources/${source.id}/revoke`, { headers });
  expect(revoked.status()).toBe(200);
  const revokedBody = await revoked.json() as { enabled: boolean };
  expect(revokedBody.enabled).toBe(false);

  const ingestAfterRevocation = await page.request.post(ingestionApi, {
    headers: { "X-Source-Id": source.id, "X-Api-Key": source.api_key ?? "missing" },
    data: { category: "authentication", outcome: "failure" },
  });
  expect(ingestAfterRevocation.status()).toBe(403);
  await page.close();
});
