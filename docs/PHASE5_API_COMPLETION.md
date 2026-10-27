# Phase 5.5 API completion — local development

Date: 2026-10-26. This report records code and checks executed in the current working tree; it is not a production-readiness declaration.

## Completed contracts

| Contract | Integration | Verification |
| --- | --- | --- |
| `GET /events` | Events workspace sends real filters, stable sort, bounded offset and limit; it renders server totals and page controls. | Query builder regression test passed; unauthenticated request returned `401`. |
| `GET /alerts/search` | Alert Triage uses server text/status/severity paging and total count. | API suite passed; unauthenticated request returned `401`. |
| `GET /responses`, `GET /responses/{id}` | Response Management lists persisted proposals, latest review and execution state, then opens the existing incident-scoped action surface. | API suite passed; unauthenticated request returned `401`. |
| `GET /audit/` | Audit Activity displays server-paged records; the API recursively redacts secret-bearing metadata fields. | Redaction regression test passed; unauthenticated request returned `401`. |
| `GET /events/dashboard/operations` | Dashboard operational posture uses backend aggregate counts and source state. | Frontend TypeScript/lint/build passed. |
| `GET /health/operations` | System Health displays direct dependency checks and explicitly unknown worker state where heartbeats do not exist. | Frontend TypeScript/lint/build passed; unauthenticated request returned `401`. |

## Data migration

`apps/api/alembic/versions/h57g8c9d0e1f_add_phase5_read_model_indexes.py` was applied successfully. Alembic reports `h57g8c9d0e1f (head)`. The migration only adds indexes on audit and response read paths.

## Security characteristics

- Existing Keycloak/JWT permission dependencies protect all new routes.
- Page limits are bounded at 250 and offsets at 100,000.
- Event sorting is allowlisted and includes a stable normalized-event-ID tie-breaker.
- No response write/approval/execution state machine changed; dry runs remain validated-only.
- Audit read requests do not expose passwords, tokens, authorization fields, cookies, or API keys in returned metadata.

## Final verification update

Authorized integration verification discovered that the existing OpenSearch mapping did not satisfy a normal full-text query for persisted `powershell` telemetry. The event query now retains `simple_query_string` and adds a case-insensitive keyword substring fallback with user wildcard characters escaped. A fresh signed-token query returned 10 matching persisted records, while a literal wildcard-input regression test passed. A controlled signed-token CSV upload also verified the new `file_hashes` CSV preservation and exact SHA-256 filtering.

The temporary Keycloak verification client used for those checks was removed immediately after the tests; no credential, token, or client secret is recorded here.

## Rule administration decision

Rule metadata may be listed/created by the existing API, but safe live editing/deployment was not added. Detection rules are file-mounted read-only into the worker and there is no validated reload/deployment acknowledgement protocol. A database-only edit would be misleading, so the Rules UI remains an honest configuration inventory.
