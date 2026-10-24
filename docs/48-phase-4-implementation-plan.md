# Phase 4 Implementation Plan

## Baseline Verification
Before beginning Phase 4, the repository baseline was verified using `.\scripts\verify.ps1`.
- **Pre-existing Failures Recorded**: 
  - Backend: `ruff format` reports 6 unformatted files. `mypy` reports 3 strict type errors in `main.py` and `config.py`. 
  - Frontend: `eslint` reports `any` types in `api.ts`. `typecheck` command is missing in `apps/web/package.json`. 
  - Global: `pre-commit` command not found (needs `pip install pre-commit`).
- **Passes**: Backend tests passed with 89% coverage.
These are Phase 3 issues and will not be attributed to Phase 4, though they may be fixed incidentally if required to pass CI.

## Infrastructure Services
| Service | Image | Profile | Host Port |
|---------|-------|---------|-----------|
| PostgreSQL | `postgres:16-alpine` | `core` | 5432 |
| OpenSearch | `opensearchproject/opensearch:2.15.0` | `core` | 9200 |
| Redpanda | `redpandadata/redpanda:v24.1.9` | `core` | 9092 |
| Redis | `redis:7-alpine` | `core` | None (Internal) |
| MinIO | `minio/minio:RELEASE.2024-07-31T15-58-33Z` | `core` | 9000, 9001 |
| OTel Collector | `otel/opentelemetry-collector-contrib:0.106.1` | `observability` | None |
| Prometheus | `prom/prometheus:v2.53.1` | `observability` | 9090 |
| Grafana | `grafana/grafana:11.1.0` | `observability` | 3001 |
| Keycloak | `quay.io/keycloak/keycloak:25.0.2` | `admin-tools` | 8082 |
| MLflow | `custom-build (mlflow 2.14.3)` | `admin-tools` | 5000 |
| OS Dashboards | `opensearchproject/opensearch-dashboards:2.15.0` | `admin-tools` | 5601 |
| RP Console | `redpandadata/console:v2.4.6` | `admin-tools` | 8081 |
| Ollama | `ollama/ollama:latest` | `llm` (Opt-in) | 11434 |

## Architecture Decisions
- **ADR-020**: Local Compose Service Layout (Profiles used).
- **ADR-021**: Infrastructure Network Isolation (`data-net`, `observability-net`, `application-net`).
- **ADR-022**: Local Secret Generation (PowerShell script, stored in `.env`).
- **ADR-023**: MLflow PostgreSQL/MinIO Architecture.
- **ADR-024**: Local Observability Stack (OTel -> Prometheus).
- **ADR-025**: Resource-Aware Compose Profiles.

## Exclusions
- Application database models (Phase 5).
- RBA / Authentication integration in frontend/backend.
- Real security events or ML artifacts.
