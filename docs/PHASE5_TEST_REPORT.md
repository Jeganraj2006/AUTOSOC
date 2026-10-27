# Phase 5 test report — Milestone 5.1

| Check | Result |
| --- | --- |
| `pnpm lint` | Passed: 0 errors, 0 warnings. |
| `pnpm exec tsc --noEmit` | Passed. |
| `pnpm exec vitest run` | Passed: 2 tests in 1 file. |
| `pnpm build` | Passed. |
| Browser interaction/E2E | Blocked: no controllable local browser tab was available. |

Known non-failing environment warnings: Vite’s future native-config warning, Next.js workspace-root warning, and Next.js middleware-to-proxy deprecation warning. No backend tests or Docker services were modified in this milestone.

## Milestone 5.2

| Check | Result |
| --- | --- |
| `pnpm lint` | Passed: 0 errors, 0 warnings after monitoring workspace changes. |
| `pnpm exec tsc --noEmit` | Passed. |
| `pnpm exec vitest run` | Passed: 7 tests in 2 files (including 5 monitoring-workspace regression tests). |
| `pnpm build` | Passed: Next.js optimized production build completed successfully (18 routes generated). |
| Authenticated browser E2E | Blocked: the supported in-app browser bridge exposed no controllable local tab. No unsupported automation was used. |

The Milestone 5.2 test additions cover API-safe event filter construction, active-alert treatment, viewer-safe triage visibility, incident route encoding, and dry-run eligibility. They do not substitute for authenticated browser E2E or backend authorization tests.

## Milestone 5.3

| Check | Result |
| --- | --- |
| `pnpm lint` | Passed: 0 errors, 0 warnings. |
| `pnpm exec tsc --noEmit` | Passed. |
| `pnpm exec vitest run` | Passed: 12 tests in 3 files. |
| `pnpm build` | Passed: Next.js optimized production build completed successfully (18 routes generated). |
| Authenticated browser E2E | Blocked: no controllable local browser tab was exposed by the supported bridge. |

New intelligence regression coverage includes rule filtering/empty results, ATT&CK reference parsing, prediction metadata and missing-estimate handling, persisted investigation states, and evidence citation de-duplication. Browser and backend authorization tests were not substituted or claimed as passed.

## Milestone 5.4

| Check | Result |
| --- | --- |
| `pnpm lint` | Passed: 0 errors, 0 warnings. |
| `pnpm exec tsc --noEmit` | Passed. |
| `pnpm exec vitest run` | Passed: 15 tests in 4 files. |
| `pnpm build` | Passed: Next.js optimized production build completed successfully (19 routes generated). |
| Browser verification | Blocked: the supported browser bridge exposes no controllable local tab. |

New tests cover viewer data-source restrictions, health-state degradation/unknown handling, and readable persisted response lifecycle states. They do not replace server-side RBAC or authenticated browser integration tests.
# Milestone 5.5 test update — 2026-10-26

| Command/check | Result |
| --- | --- |
| `apps/api: uv run --group dev pytest -q` | Passed — 19 tests. |
| `apps/api: uv run alembic upgrade head` | Passed — migrated to `h57g8c9d0e1f`. |
| `apps/web: pnpm lint` | Passed — 0 errors, 0 warnings. |
| `apps/web: pnpm exec tsc --noEmit` | Passed. |
| `apps/web: pnpm exec vitest run` | Passed — 4 files, 15 tests. |
| `apps/web: pnpm build` | Passed compilation/build artifact. Non-failing Next workspace-root/middleware warnings remain. |
| Worker suites | Passed — ingestion 5, normalization 2, detection 4, correlation 2, agents 1 (14 total). |
| Unauthenticated new routes | Passed — each returned 401. |
| Authorized API integration | Passed — temporary signed-token client verified Admin/Analyst/Viewer APIs and was removed afterward. |
| Playwright role journeys | Passed — administrator, analyst, viewer, and 375/768/1280/1920 responsive checks. |
| Fresh pipeline acceptance | Passed for local development — durable raw object, events, alerts, incidents, ATT&CK links, prediction, local-Ollama investigation, response approval/execution, and audit evidence. |
| Monolithic pipeline Playwright attempt | Failed then recovered — first attempt timed out during the original 90-second Ollama request; durable retry completed the investigation after the bound was increased to 180 seconds, and the response browser test passed. |
| Browser/Playwright journey suite | Blocked — no supported controllable local browser tab/configuration available. |
| Full browser UI flow | Blocked — the repository has no Playwright configuration and the supported browser bridge exposes no controllable tab. |
