import { expect, test, type Browser, type Page } from "@playwright/test";

const api = "http://127.0.0.1:8000/api/v1";

function identity(role: "ADMIN" | "ANALYST") {
  const username = process.env[`AUTOSOC_E2E_${role}_USERNAME`];
  const password = process.env[`AUTOSOC_E2E_${role}_PASSWORD`];
  if (!username || !password) throw new Error(`Missing protected ${role} browser-test credentials.`);
  return { username, password };
}

async function signIn(browser: Browser, user: { username: string; password: string }): Promise<Page> {
  const page = await browser.newPage();
  await page.goto("http://127.0.0.1:3000/login");
  await page.getByRole("button", { name: "Sign in with AutoSOC Identity" }).click();
  await page.locator("#username").fill(user.username);
  await page.locator("#password").fill(user.password);
  await page.locator("#kc-login").click();
  await expect(page).toHaveURL(/\/dashboard$/, { timeout: 30_000 });
  return page;
}

async function token(page: Page) {
  const value = await page.evaluate(async () => {
    const response = await fetch("/api/auth/session");
    const session: unknown = await response.json();
    return session && typeof session === "object" && "accessToken" in session && typeof session.accessToken === "string" ? session.accessToken : null;
  });
  if (!value) throw new Error("No signed browser access token was available.");
  return value;
}

test("analyst proposal receives administrator validated-only approval", async ({ browser }) => {
  const incidentId = process.env.AUTOSOC_E2E_ACCEPTANCE_INCIDENT_ID;
  test.skip(!incidentId, "Set AUTOSOC_E2E_ACCEPTANCE_INCIDENT_ID only for a freshly created synthetic incident.");
  if (!incidentId) throw new Error("Acceptance incident ID was not provided.");
  const analyst = await signIn(browser, identity("ANALYST"));
  const analystToken = await token(analyst);
  const recommendationResponse = await analyst.request.post(`${api}/incidents/${incidentId}/responses`, {
    headers: { Authorization: `Bearer ${analystToken}` },
    data: {
      incident_id: incidentId,
      source: "phase55_acceptance",
      action_type: "block_ip",
      playbook_id: "phase55-validated-only",
      target_type: "ip_address",
      target_reference: "198.51.100.0/24",
      rationale: "Fresh synthetic Phase 5.5 response validation.",
      expected_benefit: "Validate approval and audit persistence without containment.",
      evidence_references: [],
      impact: "low",
      reversibility: "reversible",
    },
  });
  expect(recommendationResponse.status()).toBe(200);
  const recommendation = await recommendationResponse.json() as { id: string };
  const reviewResponse = await analyst.request.post(`${api}/responses/${recommendation.id}/request-approval`, { headers: { Authorization: `Bearer ${analystToken}` } });
  expect(reviewResponse.status()).toBe(200);

  const admin = await signIn(browser, identity("ADMIN"));
  const adminToken = await token(admin);
  const approvalResponse = await admin.request.post(`${api}/responses/${recommendation.id}/approve`, {
    headers: { Authorization: `Bearer ${adminToken}` },
    data: { decision: "approved", reason: "Fresh synthetic Phase 5.5 approval." },
  });
  expect(approvalResponse.status()).toBe(200);
  const executionResponse = await admin.request.post(`${api}/responses/${recommendation.id}/execute`, {
    headers: { Authorization: `Bearer ${adminToken}` },
    data: { recommendation_id: recommendation.id, mode: "dry_run" },
  });
  expect(executionResponse.status()).toBe(200);
  const execution = await executionResponse.json() as { id: string; status: string; verification_status?: string; result?: { outcome?: string } };
  expect(execution.status).toBe("succeeded");
  expect(execution.verification_status).toBe("verified");
  expect(execution.result?.outcome).toBe("validated_only");

  await admin.goto("http://127.0.0.1:3000/responses");
  await expect(admin.getByRole("heading", { name: "Response management" })).toBeVisible();
  await admin.locator("#response-incident").fill(incidentId);
  await admin.getByRole("button", { name: "Apply filters" }).click();
  await expect(admin.getByText(recommendation.id)).toBeVisible();
  await analyst.close();
  await admin.close();
});
