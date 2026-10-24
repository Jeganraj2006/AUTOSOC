# AutoSOC Project Audit — Phase 1

**Audit date:** 2026-10-24  
**Repository assessed:** `E:\AUTOSOC\AUTOSOC-main`  
**Delivery input:** `C:\Users\pjega\Downloads\AutoSOC_Safety_UI_Update (1).zip`  
**Scope:** read-only repository review and baseline validation. No application source was changed in Phase 1.

## Executive assessment

This is an academic SOC prototype with a substantial FastAPI/Next.js codebase, schemas, worker scaffolding, ML datasets/models, infrastructure manifests, and UI screens. It is **not ready for a secure demonstration or production deployment**. The delivery status file accurately characterizes the ZIP as an incremental safety/UI update, rather than a completed production release.

The most urgent blockers are authentication bypasses, unauthenticated operational endpoints, false-positive health reporting, broken credential-login integration, and a disconnected/simulated worker pipeline. These prevent the required persisted, authorized SOC workflow from being verified.

The destructive bulk-purge endpoint is correctly disabled with HTTP 410. It must remain disabled.

## Audit conditions and baseline

| Item | Observed state |
| --- | --- |
| Git metadata | No `.git` directory exists in `E:\AUTOSOC` or `E:\AUTOSOC\AUTOSOC-main`; Git status and revision cannot be established. |
| Host capacity | 15.7 GB used / 89.1 GB free on `E:`; 16 GB installed RAM. |
| Installed runtimes | Python 3.14.5 is default, Python 3.12.0 is available; Node 24.20.0; pnpm 11.22.0. Repository docs require Python 3.12 and Node 20. |
| Local storage policy | All generated Phase 1 environment/cache files were directed to `E:\AUTOSOC`; no model training was run. |
| ZIP relationship | The ZIP top-level is `AUTOSOC-main` and its source-tree entries are the same set represented by the on-disk extracted delivery. Its delivery note identifies it as the safety/UI update. |
| Dependency state | `apps/web/node_modules` is absent and `next` cannot be resolved. API locked packages are not fully cached. A parent-level `E:\AUTOSOC\node_modules` is not a valid install for this nested repository. |

## Architecture and technology stack

| Layer | Intended implementation | Current assessment |
| --- | --- | --- |
| Web application | Next.js 16, React 19, TypeScript, Tailwind 4, Radix UI, React Query, ECharts, NextAuth | Screens and hooks are present; dependencies are absent and several API/auth paths are incompatible. |
| API control plane | FastAPI, Pydantic 2, SQLAlchemy async, Alembic, asyncpg, httpx | Route surface is broad, but authorization is inconsistent and error/health behavior is unsafe. |
| Data stores | PostgreSQL authoritative records, OpenSearch events, Redis state/deduplication, Redpanda event transport | No running services or migration validation were available. Several components bypass or merely describe the intended stores. |
| Workers | Ingestion, normalization, detection, ML inference, correlation, agent and response workers | Most have useful scaffolding; correlation persistence, ML inference, RAG and response execution are not proven functional. |
| ML/AI | scikit-learn anomaly flow, MLflow artifacts, Markov ATT&CK predictor, LangGraph/Ollama agents | The API Markov predictor is a static heuristic. The ML worker explicitly simulates probabilities; agent evidence contains invented/default values. |
| Infrastructure | Docker Compose, Kubernetes manifests, Keycloak configuration, setup/demo scripts | Present but not executed or verified. |

The intended event flow is: ingestion -> Redpanda raw topic -> normalization/enrichment -> normalized topic/OpenSearch -> rule/ML detection -> detection topic -> correlation -> PostgreSQL incidents -> agents/responses. The manual API event routes form a second, direct OpenSearch path, so the design has no single proven source of truth.

## API inventory and authorization review

All API routes are under `/api/v1`, except the API root `/`.

| Area | Implemented routes | Authorization / audit finding |
| --- | --- | --- |
| Health | `GET /health/live`, `/health/ready`, `/health/version` | Intentionally public, but hard-code every dependency as `ok`; they are not health checks. |
| Auth | `GET /auth/me`, `GET /auth/test-admin` | Bearer auth/permission dependency is applied, but token validation is unsafe (see Critical findings). No `/auth/token` route exists. |
| Events | `GET /events/dashboard/summary`, `GET /events/`, `GET /events/{id}`, `POST /events/upload`, `/events/seed`, `/events/packet`, `/events/detect` | **No authentication or authorization dependency on any route.** These expose event data and permit upload, seeding, packet indexing and on-demand ML training. |
| Alerts | `GET /alerts/`, `GET /alerts/{id}`, `PATCH /alerts/{id}/status` | Read endpoints require a principal; status update requires analyst/admin. Assignment/triage/evidence APIs are absent. |
| Incidents | `GET /incidents/`, `GET /incidents/{id}`, `PATCH /incidents/{id}/status`, `GET/POST /incidents/{id}/notes`, `GET /incidents/{id}/alerts` | **No authorization on any endpoint.** Mutations record actor `system`, not the requester. No timeline/evidence API. |
| Rules | `GET /rules`, `POST /rules` | Permission-gated and audited for creation. Update/delete, validation/execution state and audit coverage are absent. |
| Data sources | `GET`, `POST`, `PUT /data-sources` | Permission-gated and create/update audited. No delete, secret handling or connectivity verification API. |
| Predictions | `GET latest`, `GET history`, `POST recompute` under `/incidents/{id}/predictions` | Read requires principal; recompute requires analyst/admin. Persists static Markov output, not a verified model inference. |
| Agents | `POST`/`GET` duplicated aliases for incident investigations; `GET`/`POST cancel /agent-executions/{id}` | Mostly gated. A GET with no previous execution creates and runs an investigation, violating read-only semantics. |
| Response | create/list incident recommendations; request approval, approve, execute, rollback | Principal/role checks exist, but separation of duties, audit logging and worker handoff are incomplete. |
| System | `POST` and `DELETE /system/purge-all` | Correctly returns HTTP 410. The stale frontend helper still calls it but no dashboard control is present. |

## Frontend route and API trace

| Frontend route | API/hook use | Integration state |
| --- | --- | --- |
| `/` | Redirect/public entry | Present. |
| `/login` | NextAuth Keycloak and credentials provider | Broken credential path: it posts to `/api/v1/auth/token`, which is not implemented. Frontend default issuer uses port 8080; backend Keycloak URL uses port 8082. |
| `/dashboard` | `GET /events/dashboard/summary` | Hook passes a token, but server does not require one. It only exposes event aggregates, not the required alerts/incidents/approval/engine/agent dashboard metrics. |
| `/events`, `/events/[eventId]` | event search, detail, upload, detect | UI integration exists, but all server routes are public; direct upload/indexing bypasses the worker pipeline. |
| `/alerts`, `/alerts/[alertId]` | alert list/detail/status | Basic list/detail/status only; no assignment, evidence or complete triage workflow. |
| `/incidents`, `/incidents/[incidentId]` | incident list/detail/status/notes, agents and response panels | Hooks send tokens, but incident API ignores them. Timeline/evidence are not backed by a route. |
| `/predictions` | incidents plus prediction history/recompute | Connected to static Markov predictions; must be labelled as heuristic until real serving validation. |
| `/agents` | incidents and execution APIs | API can start work on `GET`; worker uses fixed source/destination IP defaults and synthetic agent assertions. |
| `/detection` | `POST /events/detect` | Invokes request-time `train_and_detect`; violates the no-unnecessary-retraining constraint and lacks authorization. |
| `/data-sources` | list/create/update data sources | Basic API exists; no secret-safe verification or deletion. |
| `/rules` | `GET /rules?limit=100` | This page calls `fetchApi` without the session authorization header, while the backend requires `RULES_READ`; it will return 401. |
| `/system-health` | `GET /health/live` | Renders a synthetic healthy response, not actual dependency state. |
| `/audit` | No API hook found | No audit-record endpoint exists; page cannot display persisted audit activity. |
| `/profile` | `GET /auth/me` | Dependent on the broken auth flow. |

The shell provides responsive dark/light styling, loading states and error/retry treatment on several pages. Its navigation differs from the requested organization: it uses **Threat Intelligence** and **Platform**, and does not expose the requested `User Profile` navigation item as part of Administration.

## Database, persistence, and migrations

The SQLAlchemy model package includes data sources, rules, system settings, audit logs, alerts, incidents, incident links/events/notes/timeline, ATT&CK mappings, predictions, agent executions and response records. Alembic has seven revisions from initial Phase 5 records through responses and agent executions.

Verification is blocked because the API environment could not be installed offline, and no PostgreSQL service was supplied. No migration has been run. Specific concerns:

- The documented `users` and `roles` tables/routes do not exist in the current model/route inventory; principals are token-derived.
- Event storage is OpenSearch-only; event APIs do not persist an authoritative event record in PostgreSQL.
- The correlation worker's `IncidentManager.create_incident` and `update_incident` contain `pass` where PostgreSQL writes and publishing should occur.
- Several write paths commit internally without a shared transaction/outbox, so event indexing, alert creation, incident creation and prediction persistence can partially succeed.
- `GET /incidents/{id}/agents` can synchronously create and execute work, producing a write on a read request.
- API defaults include development PostgreSQL credentials and `DEBUG=true`; production startup does not require externally supplied secrets.

## Core SOC workflow status

| Required stage | Status | Evidence / gap |
| --- | --- | --- |
| Security-event ingestion | Partial | Ingestion worker and manual CSV/packet APIs exist. Manual APIs write directly to OpenSearch and are unauthenticated. |
| Normalization | Partial | Parsers and normalized schema exist, but no end-to-end execution was possible. |
| Rule-based detection | Partial | Detection rules/tests exist; no broker/service integration was run. |
| ML-assisted detection | Not verified | `workers/ml-inference` explicitly uses simulated scores. `/events/detect` trains a service at request time. |
| Alert creation | Partial | Detection persistence models/code exist; no durable pipeline verification. |
| Alert correlation -> incident | Incomplete | Correlation worker has placeholder persistence and publishing logic. |
| Incident investigation/evidence/timeline | Partial | Records and pages exist; no timeline/evidence endpoint and incident mutations are unauthenticated. |
| AI-assisted analysis | Demonstration only | LangGraph service is present but uses fixed IPs and canned/fallback findings; RAG ingest is empty. |
| Human-approved response | Partial | Approval records, expiry and an idempotency lookup exist. There is no verified dispatch to the response worker, and an analyst can approve a recommendation without separation-of-duties protection. |
| Audit history | Partial | Some rule/data-source/incident-note/status actions write audit records. Alerts, responses, auth-sensitive actions and system access are not comprehensively audited. |

## Security findings

### Critical

1. **Authentication can be bypassed.** `auth/keycloak.py` catches JWKS or token-validation errors and decodes the token with signature verification disabled. On another decode failure it supplies a principal with `soc_analyst`, `admin`, and `analyst` roles. An attacker can obtain privileged access whenever Keycloak/JWKS is unavailable or a crafted token reaches this fallback.
2. **High-impact event operations are unauthenticated.** All event reads and writes—including upload, demo seeding, live packet indexing, and anomaly detection—lack a principal/permission dependency. They can disclose telemetry, poison event indexes, generate alert/incident data, and consume compute.

### High

1. **Incident data and mutations are unauthenticated.** Listing incidents, reading notes/alerts, changing status and adding notes require only a database session. The code records `system` as the actor, defeating accountability.
2. **The credential login flow is not backed by the API.** The frontend calls a missing token endpoint; Keycloak configuration is inconsistent between tiers. It also has a fallback NextAuth secret/dummy client secret that must be forbidden outside explicit development mode.
3. **Health endpoints are fabricated.** Liveness and readiness report database, Redis, OpenSearch and Redpanda `ok` without probing them. This can cause the UI, orchestration and operators to trust a failed system.
4. **Response authorization is insufficient for destructive actions.** An analyst/admin can create, approve and execute response work; no independent approver is enforced. Response routes do not write audit records, and the execution endpoint only creates a pending record—no verified response worker consumes it.

### Medium

1. Event routes return raw exception strings, potentially exposing OpenSearch topology and implementation details. Auto-escalation exceptions are printed and then suppressed.
2. The in-memory rate limiter is process-local, covers only a subset of mutation paths, and is unsuitable for multiple workers or resilient abuse protection.
3. Agent execution populates fixed IP addresses and canned evidence, while the ML inference worker explicitly simulates probabilities. These must be unmistakably labelled as demonstration output, not observed intelligence.
4. Rule/data-source controls lack delete/update completeness, connection validation and full audit coverage. There is no shown secret encryption/redaction design for source credentials.
5. The stale `purgeAllDatabaseRecords` client helper should be removed after consumers are confirmed absent, although the server-side HTTP 410 control is effective.

## UI/UX findings

- Strong foundations: responsive shell, dark default, persisted theme preference, status indicator, skeletons and several error/retry states.
- The dashboard does not satisfy its operational metrics brief; it is event-aggregate-only and has no pending approvals, incident/alert totals, detection-engine status, ingestion health or genuine agent status.
- Audit Activity has no data contract; Rules lacks session authorization; user profile depends on non-functional login.
- Alerts and incidents are tables/detail pages rather than full analyst workspaces: assignment, evidence, timeline and clear action feedback are incomplete.
- `apps/web/README.md` remains the default `create-next-app` text and does not explain this application, its environment or verification steps.

## Test and validation evidence

| Command / check | Result | Evidence |
| --- | --- | --- |
| `Python 3.12 -m compileall -q apps/api/src workers ml` with cache on `E:` | **Passed** | Exit code 0. This confirms Python syntax compilation only; it does not import dependencies or exercise behavior. |
| `uv run --offline --extra dev pytest` (initial default Python) | **Blocked** | Cache lacked `numpy==2.5.2` for CPython 3.14. |
| `uv sync --offline --python 3.12 --extra dev` | **Blocked** | Lock resolution succeeded but required `scipy==1.18.1` CPython 3.12 wheel was not cached. No Pytest test was collected or run. |
| Frontend dependency resolution | **Failed precondition** | `node -p "require.resolve('next/package.json')"` in `apps/web` returned `MODULE_NOT_FOUND`. No lint/typecheck/Vitest/build command can be valid until dependencies are installed. |
| `pnpm --filter web lint` | **Not a valid result** | The global pnpm wrapper stalled before invoking ESLint and was stopped. This is not recorded as a lint pass or fail. |
| Alembic migration | **Not run** | API dependencies and a PostgreSQL target were unavailable. |
| API/browser/SOC integration/security tests | **Not run** | Required services and complete dependencies were unavailable. |

Test inventory is thin for the requested scope: API has five health tests plus one AST-only purge guard; the web suite has two `fetchApi` unit tests; worker tests are distributed rather than run by a single verified command. Static inspection also shows likely existing API health-test contract failures: tests expect `AutoSOC Backend`, `alive`, `ready`, and `database=not_configured`, whereas the implementation defaults to `AutoSOC Backend API`, `healthy`, and `database=ok`.

## Prioritized remediation plan

### Phase 2 — backend stabilization (do first)

1. Remove every unsigned-token and synthetic-principal fallback. Fail closed on JWKS/token validation errors; validate issuer, audience and algorithm; implement or remove the credentials flow and align Keycloak endpoints.
2. Apply explicit permission dependencies to all event and incident routes. Attribute every mutation to the authenticated principal and add request/audit context.
3. Replace hard-coded health results with bounded probes and accurate degraded/unready states. Redact upstream errors from clients.
4. Establish a reproducible E:-resident Python 3.12/Node 20 dependency install, then repair API health tests and run the actual backend suite, lint and typecheck.
5. Verify Alembic head against a disposable PostgreSQL database; correct model/migration drift before functional writes.

### Phase 3 — durable SOC workflow

1. Choose the authoritative ingestion path and eliminate direct, unaudited bypasses. Add schema validation, source authentication, deduplication, retries and idempotency.
2. Implement correlation worker PostgreSQL persistence and outbox/event publication. Add transaction-safe alert/incident transitions and timeline/evidence APIs.
3. Complete alert assignment/triage, incident filtering/pagination, evidence retrieval and audit-history APIs; align all web hooks to their authorization contracts.

### Phase 4 — ML/agent integrity

1. Load and validate compatible persisted models; remove request-time retraining from the operational API.
2. Replace simulated inference, fixed agent context and canned evidence with source-linked output, or explicitly gate and label them as demonstration mode.
3. Implement RAG ingestion/retrieval, persist model metadata/confidence/limitations, and test graceful provider/model failure paths.

### Phase 5 — frontend completion

1. Install the locked workspace dependencies on `E:` and run lint, typecheck, Vitest and production build.
2. Repair auth propagation, Rules authorization, the audit page, required dashboard metrics, navigation grouping and complete action feedback.
3. Build evidence/timeline, approval and response UX only after their authorized backend contracts exist.

### Phase 6 — end-to-end verification

1. Test migrations, Keycloak auth/RBAC, source ingestion, normalized-event processing, rule/ML detections, correlation, agent output, approval/response and audit trail with isolated fixtures.
2. Add browser E2E coverage and negative authorization/security tests. Do not claim real ML, agent, response or health behavior until these run against real dependencies.

## Phase 1 completion status

Phase 1 is complete: the repository was inventoried, documentation and code paths were inspected, a safe baseline was attempted, concrete blockers were captured, and this audit was generated. Application code, migrations, infrastructure and the supplied ZIP have not been altered. Phase 2 requires explicit approval because it changes authentication, authorization, API and database behavior.
