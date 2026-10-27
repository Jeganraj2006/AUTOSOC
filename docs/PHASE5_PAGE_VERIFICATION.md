# Phase 5 page verification

| Route area | Existing API integration | Phase 5 UI status | Verification |
| --- | --- | --- | --- |
| Login | Keycloak/Auth.js | Redesigned | Production build passed; browser interaction blocked by unavailable controllable local tab. |
| Global shell | `useMe`, `useSystemHealth` | Redesigned | Lint/type/build passed. |
| Dashboard | `useDashboardSummary`, `useSeedDashboardTelemetry` | Header, KPI, and error-state modernization started | Lint/type/build passed. |
| Events, alerts, incidents | Existing hooks | Pending route-level modernization | Existing integrations preserved; build passed. |
| Detection, predictions, AI investigations | Existing hooks | Pending route-level modernization | Existing integrations preserved; build passed. |
| Data sources, rules, health, audit, profile | Existing hooks/API calls | Pending route-level modernization | Existing integrations preserved; build passed. |

No route is represented as browser-E2E verified in this milestone. The existing authenticated application endpoints remained reachable before the UI changes; final page-level browser verification is still required.

## Milestone 5.2 route verification

| Route area | Integrated behavior | Static/regression verification | Browser verification |
| --- | --- | --- | --- |
| Dashboard | Authenticated event summary, alerts, incidents, and live health are composed into posture cards; seed action remains development/admin gated. | Lint, strict TypeScript, Vitest, production build passed. | Blocked: no controllable local browser tab was exposed. |
| Events | Category/source-IP/limit filters, CSV ingestion, anomaly detection, result count, and event-detail navigation retained. | Query-contract unit test plus lint/type/build passed. | Blocked. |
| Alerts | Server-side status/severity filtering, result count, detail navigation, authenticated status mutation, indicators, and correlated-incident link retained. | Alert-state and RBAC helper tests plus lint/type/build passed. | Blocked. |
| Incidents | Client-side status/severity filters are labeled against API window; detail navigation and existing progressive investigation/response tabs retained. | Safe incident-route test plus lint/type/build passed. | Blocked. |

Browser E2E was not claimed. The in-app bridge reported no open controllable tabs and did not provide a tab-open API, so no browser automation bypass was attempted.

## Milestone 5.3 route verification

| Route area | Integrated behavior | Static/regression verification | Browser verification |
| --- | --- | --- | --- |
| Detection intelligence | Rule metadata, returned-window filters, rule detail, ATT&CK metadata, and actual anomaly evaluation output. | Lint/type/Vitest/production build passed. | Blocked: no controllable local browser tab. |
| Attack predictions | Authenticated latest/history/recompute hooks, incident navigation, persisted model/technique/limitation data, and role-aware mutation control. | Lint/type/Vitest/production build passed. | Blocked. |
| AI Investigation Center | Incident-scoped execution history, role-aware start, real status polling, node telemetry, stored evidence/results, and safe diagnostics. | Lint/type/Vitest/production build passed. | Blocked. |

## Milestone 5.4 route verification

| Route area | Integrated behavior | Verification | Browser |
| --- | --- | --- | --- |
| Response management | Incident selection and the existing proposal/review/decision/validated-dry-run workflow. | Lint/type/Vitest/production build passed. | Blocked: no controllable local browser tab. |
| Data sources, rules, health, account | Existing authenticated list/mutation/session/health contracts, with truthful unsupported-feature states. | Lint/type/Vitest/production build passed. | Blocked. |
| Audit activity | Explicit API-gap state; no fabricated audit entries. | Lint/type/Vitest/production build passed. | Blocked. |
# Milestone 5.5 integration update

| Workspace | Current verification |
| --- | --- |
| Dashboard | Uses backend operational aggregates; production build and TypeScript passed. |
| Events | Sends server-side query/sort/page state and renders total/page controls; lint/type checks passed. |
| Alerts | Uses `GET /alerts/search` with text, status, severity and page state; lint/type checks passed. |
| Response Management | Uses persisted global proposals, approvals, and executions; action surface remains incident-scoped. |
| Audit Activity | Uses authenticated, redacted, read-only audit records. |
| System Health | Uses direct dependency checks and displays unknown worker status honestly. |

Browser-rendered interaction verification remains blocked by the unavailable supported browser bridge; see `PHASE5_END_TO_END_VERIFICATION.md`.

Authorized API integration was subsequently completed with temporary signed Keycloak tokens for Administrator, Analyst, and Viewer. The temporary client was removed; this verifies page contracts but does not replace browser interaction coverage.
