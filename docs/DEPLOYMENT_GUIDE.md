# Local-development deployment guide

## Scope and prerequisites

Use a Windows machine with Docker Desktop running, PowerShell 7, Git, Python 3.12 with `uv`, Node 20+ and pnpm 9+. Recommended minimums for the demonstrated stack are 16 GB RAM and 30 GB free on E: or D:; local Ollama model storage and Docker Desktop may also use their own configured system locations. AutoSOC configuration, raw objects, logs, checkpoints, and release archives are placed under `E:\AUTOSOC` by default.

## First-time setup

1. Clone the source under `E:\AUTOSOC` or `D:\AUTOSOC`; install the listed prerequisites.
2. Run `pwsh scripts/initialize-local-env.ps1`. It copies `infrastructure/docker/.env.example` only if required and replaces only placeholder values with cryptographic local secrets. It never prints them.
3. Run `pwsh scripts/setup-dev.ps1`. This validates Compose, starts core services, waits for health, installs backend development dependencies, runs Alembic migrations, reconciles Keycloak, creates topics, and starts the six workers.
4. Install local Ollama and pull the configured model: `ollama pull llama3.2:3b`.
5. Run `pwsh scripts/start-local.ps1`; API is `http://127.0.0.1:8000`, UI is `http://127.0.0.1:3000`, Keycloak is `http://127.0.0.1:8080`.

Keycloak bootstrap creates development identities only when absent. Repeat setup does not change their passwords. To intentionally rotate them, set `AUTOSOC_ROTATE_DEV_PASSWORDS=true` only for that setup invocation; use the protected external credential handoff file, never source control.

## Everyday startup and validation

Run `pwsh scripts/setup-dev.ps1` after source/migration changes, then `pwsh scripts/start-local.ps1`. Check `docker compose -f infrastructure/docker/compose.yml ps`, `GET /api/v1/health/ready`, and the login page. Application output is under `E:\AUTOSOC\runtime-logs\local-app`.

The Compose file uses `E:/AUTOSOC/docker-data/minio` by default for SeaweedFS. Override only with another E: or D: path. Stop safely with `pwsh scripts/stop-local.ps1`; it preserves persistent data.
