# Phase 5 API contract gaps

This record distinguishes a UI limitation from a missing or incomplete authenticated backend contract.

## Milestone 5.5 update — 2026-10-26

The following additive, authenticated contracts are implemented and integrated in the frontend. Existing collection and incident-scoped contracts remain available for compatibility.

| Resolved gap | Contract | Guardrails |
| --- | --- | --- |
| Event query/paging | `GET /events` | Allowlisted sort fields, bounded limit/offset, total count, stable identifier tie-breaker, OpenSearch filters, `EVENTS_READ`. |
| Alert query/paging | `GET /alerts/search` | Text/ID, status, severity, incident, rule, time-range filters; bounded paging and stable order; `ALERTS_READ`. |
| Global response history | `GET /responses`, `GET /responses/{id}` | Proposal plus persisted approvals/executions, creator-filter restriction, bounded paging, `RESPONSES_READ`. |
| Audit history | `GET /audit/` | Read-only, filtered/paged, `AUDIT_READ`, recursive secret-bearing metadata redaction. |
| Dashboard aggregates | `GET /events/dashboard/operations` | Explicit 24-hour window; partial OpenSearch failure is returned rather than represented as zero. |
| Operational telemetry | `GET /health/operations` | Direct checks for dependencies/Ollama/object storage; worker health remains `unknown` without a durable heartbeat. |

Migration `h57g8c9d0e1f` adds read-only query indexes for audit and response pagination. It does not alter evidence or workflow state.

## Final acceptance correction

Data-source creation previously stored no ingestion API-key hash, leaving newly created sources unable to authenticate to the real ingestion worker. `POST /data-sources` now generates a random `asoc_` key, stores only its SHA-256 hash, and returns the cleartext key once in the creation response. List/update responses never include it. The creation dialog displays that one-time key only until the user confirms storage.

| Priority | Missing capability | Current implementation | Frontend feature blocked | Required secure backend change |
| --- | --- | --- | --- | --- |
| High | Event time range, text search, sort, cursor/offset pagination | `GET /events` accepts category, source IP, and limit. | Full SIEM query bar, time selector, sortable columns, and scalable pagination. | Add a validated query schema with allowlisted fields, bounded ranges, stable sort, opaque cursor or offset+total, and `EVENTS_READ` authorization. |
| High | Alert text search and total count | `GET /alerts/` accepts status, severity, limit, offset and returns an array. | Search and accurate result totals. | Add a validated search parameter and a paginated response envelope; preserve alert RBAC and bounded page sizes. |
| High | Dashboard pending-approval and AI-investigation aggregates | Dashboard returns event summary only. | Accurate approval queue, investigation activity, and detection-health cards. | Add an authenticated aggregate endpoint with clearly documented windows, status definitions, and no sensitive row data. |
| High | Rule execution/result relationship | `GET /rules` returns configuration metadata only. | Per-rule last execution, matching-event context, generated alerts, and related incidents. | Add a read-only, paginated rule-result endpoint keyed by rule ID with evidence references and `RULES_READ`/`ALERTS_READ` checks. |
| Medium | Rule search/filtering server-side | Rule list accepts only skip and limit. | Scalable rule inventory filtering beyond the returned window. | Add allowlisted name/type/severity/enabled filters, indexes, and a paginated response envelope. |
| High | Global prediction query | Predictions are available only for one incident. | Prediction inventory, global status totals, and cross-incident search. | Add a paginated `PREDICTIONS_READ` collection endpoint with incident association, model metadata, timestamps, status, and filters. |
| High | Complete prediction schema | Latest/history responses omit a persisted status, evidence references, trace ID, input fingerprint, and reliable confidence field. | Explainable provenance, stale status, and durable trace navigation. | Extend response schemas with typed optional fields; clearly distinguish probability/score from model confidence. |
| High | Global investigation query | Executions are available only via an incident-specific list. | Investigation Center totals, global filters, and last-run dashboard data. | Add a paginated `AGENTS_READ` collection endpoint with incident, status, timestamps, model metadata, retry count, and safe failure summary. |
| Medium | Investigation node telemetry consistency | Execution schema supports `node_statuses`/timestamps, but callers may receive no node-level data. | Fully populated accessible execution-stage visualization. | Persist each real node transition, timestamp, attempt count, and terminal status atomically; do not synthesize UI progress. |
| Medium | Safe response execution/audit read model | Existing response workflow actions are incident-scoped. | Unified read-only approval and execution history in investigation timelines. | Add a paginated, role-filtered audit/read endpoint that exposes proposal, decision, dry-run, actor, and timestamp without exposing secrets. |

## Security and pagination requirements

All new list/search endpoints should use backend RBAC as the authorization boundary, bounded input validation, stable ordering, limits appropriate to the query cost, and opaque cursors where result sets can change while analysts paginate. Aggregate endpoints should expose only counts/statistics appropriate to the caller’s permissions. The UI must not treat UI visibility as authorization.

## Milestone 5.4 additions

| Priority | Missing capability | Existing implementation | Impact and safe frontend behavior |
| --- | --- | --- |
| High | Global response lifecycle query | Recommendations are listed only through `GET /incidents/{id}/responses`. | A global response queue, approval/decision identity/timestamp, execution status, and audit history cannot be shown. The UI requires an incident selection. Add a paginated `RESPONSES_READ` endpoint with RBAC, proposal/approval/execution relationships, and audit-safe fields. |
| High | Audit activity read endpoint | Audit records are persisted but no API route lists them. | Audit Activity cannot show rows, filters, pagination, trace IDs, or navigation. Add a paginated administrator/auditor read endpoint with strict field redaction and server-side filters. |
| Medium | Detection-rule update/deployment API | Rules support list/create only. | Safe editing, validation feedback, enable/disable, and deployment confirmation cannot be offered. Add audited optimistic-concurrency update/deployment endpoints with `RULES_MANAGE`. |
| Medium | Data-source health/last-ingestion telemetry | Data-source list returns config/status/update time only. | No connection-test action, last ingestion timestamp, or metadata can be shown. Add a bounded read-only health summary endpoint; never return secrets or full connection strings. |
| Medium | Worker/AI-provider health | Health endpoint reports dependency states only. | Worker processing and Ollama availability cannot be claimed. Add explicit component readiness/processing telemetry with definitions and timestamps. |

## Remaining gaps after Milestone 5.5 implementation pass

- Detection-rule update/enable/deploy is intentionally still unavailable. The worker mounts rule files read-only and does not have a validated database-to-worker deployment/reload protocol; changing a metadata row would not safely deploy a rule.
- Rule result history, global prediction search, and global investigation search remain incident-scoped architectural gaps.
- Worker heartbeats, broker lag, retry counters, and DLQ counters are not persistently collected. The health UI therefore reports workers as `Unknown`, not healthy.
- Browser-authenticated end-to-end verification is blocked by the unavailable in-app browser bridge and by the frontend OIDC client correctly rejecting direct-grant password flow. No Keycloak setting was weakened to bypass this limitation.
