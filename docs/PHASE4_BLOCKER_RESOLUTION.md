# Phase 4 blocker resolution — fresh evidence (2026-10-26)

## Original dry-run failure

An approved dry-run request reached the real API and failed with HTTP `500` before a `response_executions` record could complete. The underlying exception was an offset-naive/offset-aware datetime comparison between PostgreSQL approval expiry values and the application’s UTC timestamp. The transaction rolled back.

## Root causes and repairs

| Defect | Repair | Files |
| --- | --- | --- |
| Approval expiry compared naive and aware datetimes | Normalize legacy naive expiry values to UTC and compare aware timestamps. | `apps/api/src/autosoc_api/api/v1/endpoints/responses.py` |
| A retry after a successful dry run was rejected because the proposal had become `executed` | Lock and return a terminal record by idempotency key before evaluating mutable proposal state. | `apps/api/src/autosoc_api/api/v1/endpoints/responses.py` |
| Body identifier could disagree with the URL identifier | Reject mismatches with HTTP `400` before lookup or execution. | `apps/api/src/autosoc_api/api/v1/endpoints/responses.py` |
| Queued dry-runs could not recover | Resume only non-terminal `dry_run` records; other modes remain queued and cannot trigger an action through a retry. | `apps/api/src/autosoc_api/api/v1/endpoints/responses.py` |
| Worker test metadata was inconsistent with the local API’s Python version | Require Python 3.12 and add opt-in development test extras; production dependencies remain unchanged. | `workers/ingestion/pyproject.toml`, `workers/correlation/pyproject.toml`, `workers/agents/pyproject.toml` |

`apps/api/tests/test_response_execution_regressions.py` covers expiry normalization and terminal/non-terminal idempotency classification. `workers/ingestion/tests/test_pipeline.py` now asserts the retry cap and capped exponential schedule.

## Fresh authenticated API evidence

Valid Keycloak tokens were obtained through a temporary test client, removed after the run. Token values and credentials were never written to source, logs, or this report.

| Scenario | HTTP result | Persistence result |
| --- | --- | --- |
| Administrator rejects an analyst proposal | `200` | Rejection audit persisted; no execution record. |
| Execute rejected proposal | `400` | No successful execution record. |
| Analyst executes pending proposal | `400` | No execution record. |
| Viewer create / approve / execute | `403` / `403` / `403` | No mutation. |
| Unauthenticated execution | `401` | No mutation. |
| Sequential duplicate approved dry-run | `200`, `200` | One succeeded execution. |
| Concurrent duplicate approved dry-run | `200`, `200` | One succeeded execution. |
| Mismatched body and path identifiers | `400` | No execution. |
| Stale queued dry-run | `200` | Same record became succeeded exactly once. |

PostgreSQL query evidence for the concurrent scenario shows one `response_executions` row for proposal `c815b2ab-c910-43af-828b-e01645fe8f04`: execution `f3f6e227-7494-4192-8b92-d3e46d7f7e93`, `dry_run`, `succeeded`, executor `dry_run_validator`, idempotency key `<proposal-id>_dry_run`, plus one `response.execution_requested` audit record attributed to `autosoc_admin`.

## Commands and current result

Fresh commands are recorded in [PHASE4_FINAL_ACCEPTANCE.md](PHASE4_FINAL_ACCEPTANCE.md). All backend, worker, lint, type, unit, and production-build checks passed. The API was restarted from the repaired source before the final duplicate/concurrency verification.

## Remaining blockers

None for the local-development Phase 4 response-approval acceptance scope. Production readiness remains blocked on intentional out-of-scope work: external-action integration, chaos testing, operational monitoring, and browser E2E coverage.
