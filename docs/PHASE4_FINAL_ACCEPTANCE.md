# Phase 4 final acceptance — local development

**Decision: ACCEPTED for local development on 2026-10-26.** This is not a production-readiness claim. The tests used isolated synthetic records and `dry_run` only; no containment connector or external destructive action was invoked.

## Authentication and response-approval acceptance

The checks used fresh synthetic proposals and real, short-lived Keycloak tokens for the existing administrator, analyst, and viewer users. A temporary, direct-grant test client was created only for this verification and removed afterward. No password, token, or client secret is recorded here.

| Case | Result | Evidence |
| --- | --- | --- |
| Analyst creates a proposal and requests approval | Passed | API success; recommendation and approval audit rows persisted. |
| Administrator rejects a proposal | Passed | `200`; proposal `fa8b8b0d-9e99-4a91-8055-95752aba0cd0` is `rejected`. |
| Rejected proposal cannot execute | Passed | `400 Execution requires an approved recommendation`; zero execution rows. |
| Pending proposal cannot execute | Passed | Analyst request returned `400 Execution requires an approved recommendation`; proposal remains `pending_review` with zero execution rows. |
| Viewer cannot propose, approve, or execute | Passed | Each real-token request returned `403 Not enough permissions`. |
| Unauthenticated execution | Passed | `401 Not authenticated`. |
| Sequential same-key retry | Passed | Both requests returned `200`; proposal `9b2c4edb-1bbb-4910-ad21-dde8c0d17750` has one succeeded execution. |
| Concurrent same-key retry | Passed | Both requests returned `200`; proposal `c815b2ab-c910-43af-828b-e01645fe8f04` has one succeeded execution. |
| Conflicting body/path proposal identifiers | Passed | `400 Recommendation ID mismatch`; no action executed. |
| Stale queued dry-run recovery | Passed | A seeded non-terminal dry-run record resumed to `succeeded` exactly once; non-dry-run actions are not auto-resumed. |
| Execution audit attribution | Passed | The concurrent record has one `response.execution_requested` entry by `autosoc_admin`. |

Database evidence for the concurrent case: execution `f3f6e227-7494-4192-8b92-d3e46d7f7e93`, mode `dry_run`, status `succeeded`, executor `dry_run_validator`, deterministic key `<proposal-id>_dry_run`, and exactly one associated execution-request audit row. Its result is `validated_only`; no containment action was attempted.

## Worker verification

Worker tests ran from E:-based isolated `uv` development environments. Production images were not changed and do not contain pytest.

| Worker suite | Result | Coverage of this acceptance |
| --- | --- | --- |
| Ingestion | 5 passed | validation DLQ, duplicate suppression, archive failure metadata, bounded retry cap, exponential/capped backoff. |
| Normalization | 2 passed | synthetic parser behavior. |
| Detection | 4 passed | deterministic rules and state contracts. |
| Correlation | 2 passed | safe lifecycle and callable worker contract with configured database URL. |
| AI investigation | 1 passed | deterministic evidence-preserving node behavior and action limitation. |

The existing retry-state implementation is used by normalization, detection, correlation, prediction, and agent workers. A full infrastructure-outage/chaos scenario was not run in this acceptance pass; that remains a production-hardening activity.

## Regression results

| Command | Result |
| --- | --- |
| `apps/api: uv run --group dev pytest -q` | 16 passed |
| `workers/ingestion: uv run --extra dev pytest -q` | 5 passed |
| `workers/normalization: uv run --with pytest pytest -q` | 2 passed |
| `workers/detection: uv run --extra dev pytest -q` | 4 passed |
| `workers/correlation: uv run --extra dev pytest -q` | 2 passed |
| `workers/agents: uv run --extra dev pytest -q` | 1 passed |
| `apps/web: pnpm lint` | passed; 0 errors, 0 warnings |
| `apps/web: pnpm exec tsc --noEmit` | passed |
| `apps/web: pnpm exec vitest run` | 2 passed |
| `apps/web: pnpm build` | passed |

Test count: **32 passed** (16 backend, 14 worker, 2 frontend unit). The backend emitted six existing dependency/schema deprecation warnings. The frontend build emitted non-failing workspace-root and middleware-convention warnings; neither changes the acceptance result.

## Remaining limitations

- No real containment operation was tested or enabled.
- No broker/database outage chaos test was run.
- Browser E2E automation was not rerun in this pass; real Keycloak-authenticated API flows, the running frontend baseline, and the production build were verified instead.
- Phase 5/UI redesign has not started.
