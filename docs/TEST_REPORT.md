# Test report — Phase 4 acceptance (2026-10-26)

> Superseded for release tracking by the Phase 6 section below; the Phase 4 evidence is preserved unchanged.

## Passed

| Area | Result |
| --- | --- |
| Keycloak-authenticated response approval, rejection, pending protection, viewer RBAC, unauthenticated protection | Passed |
| Dry-run execution persistence and audit attribution | Passed |
| Sequential, concurrent, conflict, and stale-record idempotency behavior | Passed |
| Backend test suite | 16 passed |
| Worker test suites | 14 passed |
| Frontend ESLint | 0 errors, 0 warnings |
| Frontend TypeScript | Passed |
| Frontend Vitest | 2 passed |
| Frontend production build | Passed |

Total automated tests passed: **32**.

## Test environment

- All project test environments were created beneath the project on `E:`; no production image or Docker volume was modified for testing.
- Worker tests used isolated development environments; pytest was not added to production container images.
- Response scenarios used fresh synthetic database records, valid Keycloak tokens, and dry-run mode only.
- The temporary Keycloak testing client was removed after verification.

## Warnings and limitations

- Backend pytest emitted six existing deprecation warnings from dependencies/schema configuration.
- Vitest emitted one non-failing future Vite configuration warning.
- The Next.js build emitted existing non-failing workspace-root and middleware-convention warnings.
- No external containment action, failure-infrastructure chaos test, or browser E2E suite was run in this pass.

See [PHASE4_FINAL_ACCEPTANCE.md](PHASE4_FINAL_ACCEPTANCE.md) for the full acceptance matrix and [PHASE4_BLOCKER_RESOLUTION.md](PHASE4_BLOCKER_RESOLUTION.md) for the repaired defects and database evidence.

## Phase 6 release verification (in progress)

| Check | Current result |
| --- | --- |
| Backend pytest after Phase 6 changes | 23 passed, 6 deprecation warnings |
| Phase 6 credential/LLM regression subset | 4 passed, 1 Pydantic deprecation warning |
| Existing worker suites | 14 passed (accepted baseline) |
| Worker suites rerun | 14 passed (ingestion 5, normalization 2 via isolated `uv --with` environment, detection 4, correlation 2, agents 1) |
| Frontend quality after Next.js security update | ESLint passed; TypeScript passed; Vitest 15 passed (one existing Vite future-config warning); production build compiled successfully and emitted a new `BUILD_ID` |
| Docker inventory | 12 services observed up during Phase 6 audit |
| Patched-runtime browser OIDC/responsive suite | 7 passed after Chromium was installed under `E:\AUTOSOC\playwright-browsers` |
| Browser response approval/dry run | 1 passed |
| Browser data-source key lifecycle | 1 passed: one-time key response, list redaction, revocation, and post-revocation ingestion denial |
| Fresh monolithic browser pipeline | Failed: generic waiter timed out; database/OpenSearch evidence verified raw archive, 6 normalized events, correlated incident, prediction, and completed Ollama investigation. This remains a failed browser test. |
| Production dependency audit | 0 critical, 0 high, 0 moderate, 0 low after the security updates |

## Final release verification (2026-10-27)

| Check | Result |
| --- | --- |
| Backend pytest | 24 passed; 6 known deprecation warnings |
| Worker tests | 15 passed: ingestion 5, normalization 2, detection 5, correlation 2, agents 1 |
| ESLint / TypeScript | Passed; ESLint emitted 0 errors and 0 warnings |
| Vitest | 15 passed in 4 files; one existing Vite future-config warning |
| Production build | Passed; Next.js emitted workspace-root and middleware-convention warnings |
| Full Playwright suite | 9 passed, 1 intentional data-dependent skip |
| Fresh browser SOC pipeline | Passed: source → six events → four alert links → incident → prediction → completed Ollama investigation → analyst proposal → administrator approval → validated-only execution → audit → browser record |

The final browser pipeline repair is documented in `FINAL_RELEASE_VERIFICATION.md`. No real containment action was performed.
