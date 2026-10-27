# Phase 5.5 browser E2E report — 2026-10-26

Playwright 1.62.1 was already declared by `apps/web`; Chromium was installed under `E:\AUTOSOC\playwright-browsers` and all reports, traces, video, and screenshots are written under `E:\AUTOSOC\runtime-logs\playwright-phase55`.

| Journey | Result | Evidence |
| --- | --- | --- |
| Administrator OIDC dashboard/pages/search/pagination/logout | Passed | Real Keycloak authorization-code sign-in; dashboard, events, alerts, incidents, investigations, responses, audit, health, event query, and logout. |
| Analyst read/review RBAC | Passed | Real OIDC session; incident/response views load and no administrator approve control is available. |
| Viewer read-only RBAC | Passed | Real OIDC session; permitted pages load and Audit Activity navigation is hidden. |
| Mobile 375px | Passed | Mobile menu opens; Escape now dismisses it; no document horizontal overflow; keyboard focus remains visible. |
| Tablet 768px, laptop 1280px, desktop 1920px | Passed | No document horizontal overflow and keyboard focus check passed. |
| Analyst proposal -> administrator approval -> dry run | Passed | Browser sessions used real roles; execution returned `succeeded`, `verified`, and `validated_only`; response history rendered the new proposal. |

The first monolithic fresh-pipeline Playwright attempt is retained as a failed artifact because the original 90-second local-Ollama timeout elapsed before its polling window. The worker persisted a recoverable record, retried successfully after the timeout adjustment, and the remaining approval/execution browser journey passed against that same fresh incident. This is recorded as a repaired retry-path result, not as an erased test failure.

The first mobile run found that Escape did not dismiss the navigation dialog. `apps/web/src/components/layout/shell.tsx` now listens for Escape only while the menu is open; the four responsive tests then passed.

No credentials, generated ingestion keys, or tokens were written to test source, Git, screenshots, traces, or reports.
