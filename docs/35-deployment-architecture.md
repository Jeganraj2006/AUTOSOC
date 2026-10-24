# Deployment Architecture

AutoSOC supports two deployment models: a lightweight local model for development/MVP and a production-style Kubernetes model.

*(Note: No actual Kubernetes YAML files are generated in Phase 2; this is architectural design only).*

## 1. Local Development Architecture (Docker Compose)
- **File**: `docker-compose.yml`
- **Networking**: Single custom bridge network (`autosoc-net`).
- **Storage**: Local Docker volumes for PostgreSQL, OpenSearch, Redpanda, Redis, and MinIO data persistence.
- **Components Included**:
  - `frontend` (Next.js, Port 3000)
  - `api` (FastAPI, Port 8000)
  - `worker-pipeline` (Runs ingestion, norm, detection consumers)
  - `worker-agent` (Runs LangGraph/LLM tasks)
  - `postgres`, `opensearch`, `redpanda`, `redis`, `minio`, `keycloak`
  - `ollama` (If local hardware permits, binds to host GPU if available)
  - `otel-collector`, `prometheus`, `grafana`
- **Scaling**: Fixed at 1 replica per service for simplicity.

## 2. Production-Style Architecture (Kubernetes)
- **Namespaces**:
  - `autosoc-core`: API, UI, Workers.
  - `autosoc-data`: Postgres, OS, Redpanda, Redis, MinIO.
  - `autosoc-auth`: Keycloak.
  - `autosoc-ai`: Ollama, MLflow.
  - `autosoc-obs`: Prometheus, Grafana, OTel.
- **Ingress**: NGINX Ingress Controller terminating TLS, routing `/api` to the FastAPI service and `/` to the Next.js service. Keycloak exposed on a dedicated subdomain.
- **Deployments (Stateless)**:
  - `api-deployment` (HPA enabled based on CPU).
  - `worker-ingest-deployment` (HPA based on Redpanda lag).
  - `worker-proc-deployment` (HPA based on Redpanda lag).
  - `frontend-deployment`.
- **StatefulSets (Stateful)**:
  - `postgres-sts`, `opensearch-sts`, `redpanda-sts`. All backed by PersistentVolumeClaims (PVCs).
- **Configuration & Secrets**:
  - `ConfigMaps` for environment variables (e.g., Redpanda broker URLs).
  - `Secrets` for database passwords and external API keys (integrated with a CSI secret provider).
- **Security Contexts (Pod Security)**:
  - `runAsNonRoot: true` for all AutoSOC application pods.
  - `readOnlyRootFilesystem: true` where applicable.
- **Network Policies**:
  - Default deny-all.
  - Explicit allow: `api` -> `postgres`, `workers` -> `redpanda`, `workers` -> `ollama`, etc. The `frontend` pod cannot talk directly to `postgres`.
- **Probes**:
  - Liveness and Readiness probes configured for all deployments targeting the `/health` API endpoints.
- **Backup**:
  - CronJobs configured to run `pg_dump` and sync to MinIO/external S3.
