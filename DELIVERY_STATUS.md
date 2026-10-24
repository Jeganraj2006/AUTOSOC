# AutoSOC — Updated Source Delivery

## Implemented in this package
- Disabled the unauthenticated bulk data purge API (POST and DELETE now return HTTP 410).
- Removed destructive purge control and its confirmation dialog from the dashboard.
- Grouped desktop sidebar navigation into Monitoring, Threat Intelligence, Platform, and Administration.
- Set dark theme as the default for new browser sessions; saved user preference is preserved.
- Made the environment indicator reflect Next.js build environment.

## Verification performed
- Python source compilation of modified API endpoint: passed.
- Static inspection of changed UI files and API endpoint: performed.
- Full backend integration tests, frontend TypeScript/lint/build, browser E2E tests, deployment, database migration and ML validation: NOT performed in this environment.

## Known limitations and required work
- Do not treat this package as production-ready. Verify all authorization dependencies across the remaining API endpoints, especially response execution and admin actions.
- Verify frontend build and lint after installing dependencies, and run Pytest and Playwright in a reproducible environment.
- Validate event ingestion, OpenSearch, PostgreSQL migrations, model loading, agent workflows and alert/incident/response lifecycles with real fixtures.
- Backups, secure secrets, rate limiting, monitoring, deployment hardening and performance tests require independent validation.
- A comprehensive redesign of every page was not completed; existing pages remain intact.

## Windows installation notes
Use D: or E: only for project files, dependency stores, caches, virtual environments, temporary files and build output. Do not use C: or S: for these items. Configure Windows TEMP/TMP, npm/pnpm stores, Python caches and Docker storage accordingly before installation.

This is an incremental safety/UI update to the supplied source archive, not a certified final production release.
