# Environment recovery

## Scope and storage

All project caches and local development state used during recovery are on `E:`. Docker
Desktop's configured WSL data directory is `D:\DockerDesktopWSL`; no project state was
moved to `C:`.

## Connectivity findings

| Path | Result | Recovery decision |
| --- | --- | --- |
| PyPI index and locked Windows CPython 3.12 wheel | HTTPS succeeded | Used `uv sync` with the existing `uv.lock`, a 120-second timeout, and one concurrent download. |
| npm registry metadata | `npm ping` succeeded | Metadata availability alone is insufficient. |
| npm package tarballs | TLS connections reset in pnpm, curl, and Windows web requests | No TLS bypass was used. The locked packages already present in `E:\.pnpm-store` were installed offline with `pnpm install --frozen-lockfile --offline --store-dir E:\.pnpm-store`. |
| Docker Registry authentication from Windows and Docker Desktop WSL | HTTPS and registry challenge succeeded | Docker Desktop uses its internal proxy at `http.docker.internal:3128`; image pulls were retried only after validation. |
| Original Docker dependencies | Redpanda used `latest`; Docker Hub MinIO reference no longer pulled | Redpanda is pinned to `v26.2.6`; MinIO is pinned to the official Quay release image. |

The Docker engine previously failed during a Docker Hub token redirect with a TLS-handshake
timeout. This was not reproduced by direct Windows or WSL connectivity probes. If image
pulls fail again, inspect Docker Desktop's internal proxy and local TLS-interception/AV
configuration before retrying; do not disable certificate validation or use insecure
registries.

## Local configuration

`infrastructure/docker/.env`, `apps/api/.env`, and `apps/web/.env.local` are local-only
files ignored by Git. They contain unique development values, not the former embedded
passwords. Copy the matching `.env.example` files to create a new local environment.

The compose services bind their host ports to `127.0.0.1`, avoiding accidental LAN exposure.
The compose file now requires explicit values for PostgreSQL, Keycloak, and MinIO credentials.

## Verified recovery steps

1. `uv sync --extra dev` completed from `apps/api` using the lockfile.
2. `pnpm install --frozen-lockfile --offline --store-dir E:\.pnpm-store` completed from the repository root.
3. `docker compose -f infrastructure/docker/compose.yml config --quiet` passed.
4. PostgreSQL started on `127.0.0.1:5433` and Alembic migrated it to revision `b01c2d3e4f5g`.

## Service startup order

Start only the backing services required by the API first: PostgreSQL, Redis, OpenSearch,
and Redpanda. Keycloak is needed for browser sign-in. MinIO and the worker containers are
not prerequisites for API process startup and should be started after the core services are
healthy.

```powershell
docker compose -f infrastructure/docker/compose.yml up -d postgres redis opensearch redpanda keycloak
uv run --project apps/api --offline python scripts/setup_keycloak.py
Set-Location E:\AUTOSOC\AUTOSOC-main\apps\api
uv run --offline uvicorn --app-dir src autosoc_api.main:app --host 127.0.0.1 --port 8000
Set-Location E:\AUTOSOC\AUTOSOC-main
pnpm --filter web dev
```
