# Test report

## Passed

| Check | Result |
| --- | --- |
| Backend dependency recovery | `uv sync --extra dev` completed with the existing `uv.lock`. |
| Backend tests | 13 passed: health, destructive-purge contract, missing/invalid/expired token behavior, RBAC denial, and configuration validation. |
| Backend syntax | `python -m compileall -q src tests` passed. |
| Frontend install | Frozen offline PNPM install completed using the existing E: package store. |
| Frontend unit tests | Vitest: 1 file, 2 tests passed. |
| Frontend production build | Next.js 16.3.0 production build passed. |
| Compose validation | `docker compose config --quiet` passed. |
| PostgreSQL and migrations | PostgreSQL is healthy and Alembic applied all migrations through `b01c2d3e4f5g`. |
| API runtime | `/api/v1/health/live` returns `alive`; readiness reflects live dependency state. |

At verification time, PostgreSQL, Redis, and Redpanda were healthy. The live API reported
those dependencies as `ok`; it returned 503 because OpenSearch was unavailable. The Next.js
login page returned HTTP 200 at `http://127.0.0.1:3000/login`.

## Known non-blocking checks

The repository-wide Python Ruff command reports a pre-existing 871 findings across unrelated
modules. The frontend ESLint command reports 23 errors and 23 warnings in pre-existing UI and
hook files (primarily explicit `any`, hook ordering, and escaped-entity rules). These are not
introduced by the Phase 2 authentication/authorization changes; the frontend still compiles,
type-checks, and produces a production build.

Next.js reports that the existing `middleware` convention is deprecated in favor of `proxy`.
This is a compatibility follow-up, not a build blocker.

Docker image transfers for Keycloak and OpenSearch stalled after partially downloading, even
though direct Docker Desktop WSL access to the Keycloak Quay manifest returned HTTP 200. The
Docker engine uses `http.docker.internal:3128`; investigate that internal proxy or a local
TLS-interception/endpoint-control product before retrying those large pulls. No insecure
registry, certificate bypass, or unpinned image workaround was used.
