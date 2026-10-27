import { expect, test, type APIResponse, type Browser, type Page } from "@playwright/test";
import { writeFile } from "node:fs/promises";

const appApi = "http://127.0.0.1:8000/api/v1";
const verificationApi = "http://127.0.0.1:8004/api/v1";
const ingestionApi = "http://127.0.0.1:8001/api/v1/ingest/events";

type Identity = { username: string; password: string };
type ProvisionedSource = { id: string; api_key: string };
type Incident = { id: string; primary_entities?: Array<{ type?: string; value?: string }>; correlation_rule_ids?: string[] };
type Recommendation = { id: string };

function identity(role: "ADMIN" | "ANALYST"): Identity {
  const username = process.env[`AUTOSOC_E2E_${role}_USERNAME`];
  const password = process.env[`AUTOSOC_E2E_${role}_PASSWORD`];
  if (!username || !password) throw new Error(`Missing protected ${role} browser-test credentials.`);
  return { username, password };
}

async function signedInPage(browser: Browser, user: Identity): Promise<Page> {
  const page = await browser.newPage();
  await page.goto("http://127.0.0.1:3000/login");
  await page.getByRole("button", { name: "Sign in with AutoSOC Identity" }).click();
  await page.locator("#username").fill(user.username);
  await page.locator("#password").fill(user.password);
  await page.locator("#kc-login").click();
  await expect(page).toHaveURL(/\/dashboard$/, { timeout: 30_000 });
  return page;
}

async function accessToken(page: Page): Promise<string> {
  const token = await page.evaluate(async () => {
    const response = await fetch("/api/auth/session");
    const session: unknown = await response.json();
    if (!session || typeof session !== "object" || !("accessToken" in session)) return null;
    const value = session.accessToken;
    return typeof value === "string" ? value : null;
  });
  if (!token) throw new Error("The signed-in browser session did not expose an access token for backend requests.");
  return token;
}

async function expectJson(response: APIResponse, expectedStatus = 200): Promise<unknown> {
  expect(response.status()).toBe(expectedStatus);
  return response.json();
}

async function waitFor<T>(
  operation: () => Promise<T | null>,
  description: string,
  timeoutMs = 100_000,
): Promise<T> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const result = await operation();
    if (result) return result;
    await new Promise((resolve) => setTimeout(resolve, 1_000));
  }
  throw new Error(`Timed out waiting for ${description}.`);
}

test("fresh synthetic event reaches the authenticated SOC workflow", async ({ browser }, testInfo) => {
  test.setTimeout(420_000);
  const marker = `phase55-${Date.now()}`;
  const sourceIp = `198.51.100.${Math.floor(Math.random() * 180) + 50}`;
  const adminPage = await signedInPage(browser, identity("ADMIN"));
  const adminToken = await accessToken(adminPage);

  const sourceResponse = await adminPage.request.post(`${verificationApi}/data-sources`, {
    headers: { Authorization: `Bearer ${adminToken}` },
    data: {
      name: `${marker}-source`,
      source_type: "synthetic",
      environment: "development",
      description: "Isolated Phase 5.5 browser and pipeline acceptance source.",
      enabled: true,
    },
  });
  const provisioned = await expectJson(sourceResponse, 200) as ProvisionedSource;
  expect(provisioned.id).toBeTruthy();
  expect(provisioned.api_key).toMatch(/^asoc_/);

  const failureEvents = Array.from({ length: 5 }, (_, index) => JSON.stringify({
    category: "authentication",
    type: "login",
    action: "login",
    outcome: "failure",
    user: "administrator",
    host: `${marker}-host`,
    src_ip: sourceIp,
    dst_ip: "10.55.0.20",
    timestamp: new Date(Date.now() + index).toISOString(),
    sequence: index,
  }));
  const successfulLogin = JSON.stringify({
    category: "authentication",
    type: "login",
    action: "login",
    outcome: "success",
    user: "administrator",
    host: `${marker}-host`,
    src_ip: sourceIp,
    dst_ip: "10.55.0.20",
    timestamp: new Date().toISOString(),
    sequence: "success",
  });
  const ingestionResponse = await adminPage.request.post(`${ingestionApi}/batch`, {
    headers: { "X-Source-Id": provisioned.id, "X-Api-Key": provisioned.api_key },
    data: { events: [...failureEvents, successfulLogin] },
  });
  const ingestion = await expectJson(ingestionResponse, 200) as { accepted: number; events: Array<{ event_id?: string }> };
  expect(ingestion.accepted).toBe(6);

  const duplicateResponse = await adminPage.request.post(`${ingestionApi}/batch`, {
    headers: { "X-Source-Id": provisioned.id, "X-Api-Key": provisioned.api_key },
    data: { events: [failureEvents[0]] },
  });
  const duplicate = await expectJson(duplicateResponse, 200) as { accepted: number; duplicates: number };
  expect(duplicate.accepted).toBe(0);
  expect(duplicate.duplicates).toBe(1);

  const incident = await waitFor(async () => {
    const response = await adminPage.request.get(`${appApi}/incidents/?limit=100`, { headers: { Authorization: `Bearer ${adminToken}` } });
    if (!response.ok()) return null;
    const incidents = await response.json() as Incident[];
    return incidents.find((candidate) => candidate.primary_entities?.some((entity) => entity.value === sourceIp) && candidate.correlation_rule_ids?.includes("corr_001_bruteforce_success")) ?? null;
  }, "the correlated incident");

  const indexed = await waitFor(async () => {
    const response = await adminPage.request.get(`${appApi}/events/?source_ip=${encodeURIComponent(sourceIp)}&limit=20`, { headers: { Authorization: `Bearer ${adminToken}` } });
    if (!response.ok()) {
      const body = await response.text();
      throw new Error(`Event search returned HTTP ${response.status()}: ${body.slice(0, 500)}`);
    }
    const result = await response.json() as { total?: number };
    return (result.total ?? 0) >= 6 ? result : null;
  }, "the indexed normalized events");
  expect(indexed.total).toBeGreaterThanOrEqual(6);

  const alertResponse = await adminPage.request.get(`${appApi}/incidents/${incident.id}/alerts`, { headers: { Authorization: `Bearer ${adminToken}` } });
  const alerts = await expectJson(alertResponse, 200) as Array<{ id: string }>;
  expect(alerts.length).toBeGreaterThanOrEqual(3);

  const prediction = await waitFor(async () => {
    const response = await adminPage.request.get(`${appApi}/incidents/${incident.id}/predictions/latest`, { headers: { Authorization: `Bearer ${adminToken}` } });
    return response.ok() ? response.json() : null;
  }, "the persisted prediction");
  expect(prediction).toBeTruthy();

  const investigation = await waitFor(async () => {
    const response = await adminPage.request.get(`${appApi}/incidents/${incident.id}/agents`, { headers: { Authorization: `Bearer ${adminToken}` } });
    if (!response.ok()) return null;
    const executions = await response.json() as Array<{ id: string; status: string; model_provider?: string }>;
    return executions.find((execution) => execution.status === "completed" && execution.model_provider?.includes("Ollama")) ?? null;
  }, "the completed local Ollama investigation", 300_000);

  const analystPage = await signedInPage(browser, identity("ANALYST"));
  const analystToken = await accessToken(analystPage);
  const proposalResponse = await analystPage.request.post(`${appApi}/incidents/${incident.id}/responses`, {
    headers: { Authorization: `Bearer ${analystToken}` },
    data: {
      incident_id: incident.id,
      source: "phase55_acceptance",
      action_type: "block_ip",
      playbook_id: "phase55-validated-only",
      target_type: "ip_address",
      target_reference: sourceIp,
      rationale: `Isolated ${marker} response validation.`,
      expected_benefit: "Validate the reviewed response lifecycle without containment.",
      evidence_references: alerts.map((alert) => alert.id),
      impact: "low",
      reversibility: "reversible",
    },
  });
  const proposal = await expectJson(proposalResponse, 200) as Recommendation;
  const requestReview = await analystPage.request.post(`${appApi}/responses/${proposal.id}/request-approval`, { headers: { Authorization: `Bearer ${analystToken}` } });
  await expectJson(requestReview, 200);

  const approvalResponse = await adminPage.request.post(`${appApi}/responses/${proposal.id}/approve`, {
    headers: { Authorization: `Bearer ${adminToken}` },
    data: { decision: "approved", reason: "Isolated Phase 5.5 validated-only approval." },
  });
  await expectJson(approvalResponse, 200);
  const executionResponse = await adminPage.request.post(`${appApi}/responses/${proposal.id}/execute`, {
    headers: { Authorization: `Bearer ${adminToken}` },
    data: { recommendation_id: proposal.id, mode: "dry_run" },
  });
  const execution = await expectJson(executionResponse, 200) as { id: string; status: string; verification_status?: string; result?: { outcome?: string } };
  expect(execution.status).toBe("succeeded");
  expect(execution.verification_status).toBe("verified");
  expect(execution.result?.outcome).toBe("validated_only");

  await adminPage.goto(`http://127.0.0.1:3000/responses`);
  await expect(adminPage.getByRole("heading", { name: "Response management" })).toBeVisible();
  await adminPage.locator("#response-incident").fill(incident.id);
  await adminPage.getByRole("button", { name: "Apply filters" }).click();
  await expect(adminPage.getByText(proposal.id)).toBeVisible();

  await writeFile(testInfo.outputPath("pipeline-evidence.json"), JSON.stringify({
    marker,
    source_id: provisioned.id,
    source_ip: sourceIp,
    normalized_event_ids: ingestion.events.map((event) => event.event_id).filter(Boolean),
    incident_id: incident.id,
    alert_count: alerts.length,
    investigation_id: investigation.id,
    proposal_id: proposal.id,
    execution_id: execution.id,
  }, null, 2));
  await analystPage.close();
  await adminPage.close();
});
