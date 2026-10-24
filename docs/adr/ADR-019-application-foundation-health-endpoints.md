# ADR-019: Application Foundation Health Endpoints

## Status
Accepted

## Context
In a Kubernetes or Docker Compose environment, the orchestrator needs to know if a service is running (Liveness) and if it is ready to serve traffic (Readiness).

## Decision
The FastAPI control plane will expose two distinct endpoints:
- `/api/v1/health/live`: Returns 200 OK immediately if the web server process is accepting connections. Does not check dependencies.
- `/api/v1/health/ready`: Checks connections to downstream dependencies (PostgreSQL, OpenSearch, Redpanda) and returns 200 OK only if the critical path is functional.

## Positive Consequences
- Prevents Kubernetes from infinitely restarting a pod that is waiting for a database to initialize (Liveness probe passes, Readiness fails).
- Provides clear diagnostic information via the JSON payload showing exactly which component is failing.

## Negative Consequences
- Slightly more complex logic to maintain in the health endpoint.

## Security Implications
- The health endpoints must not leak sensitive version strings of underlying databases in the error payloads. Only "ok" or "error" statuses should be returned for dependencies.
