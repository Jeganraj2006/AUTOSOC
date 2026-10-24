# ADR-001: Modular Monolith with Background Workers

## Status
Accepted

## Context
AutoSOC requires a complex control plane and several data processing tasks (ingestion, detection, ML inference, agent execution). A fully microservices-based architecture would introduce significant operational overhead, deployment complexity, and distributed tracing requirements prematurely for a Phase 1 MVP and academic project. However, blocking the main API thread with long-running tasks like ML inference or log processing is unacceptable.

## Decision
We will adopt a modular-monolith architecture for the control-plane API (FastAPI) and separate the heavy, asynchronous processing into independent background workers. These workers will communicate primarily via Redpanda (for event streaming) and share access to PostgreSQL/OpenSearch where strictly necessary for the MVP.

## Alternatives Considered
- **Microservices**: Rejected due to premature complexity, operational overhead, and distributed transaction challenges for an MVP.
- **Single Monolith (No external workers)**: Rejected because event processing, ML inference, and LLM orchestration would block API requests and lead to severe latency and timeout issues.

## Positive Consequences
- Simplified deployment (fewer services to orchestrate initially).
- Easier debugging and tracing within the control plane.
- Asynchronous tasks run independently without blocking API responses.
- Allows for logical separation of domains (modules) that can be split into microservices later if scale demands.

## Negative Consequences
- Workers might share database access initially, which couples them at the data layer.
- Some shared libraries might become a bottleneck for deployment.

## Security Implications
- Module boundaries must be enforced logically within the codebase to prevent privilege escalation or data leakage across domains.

## Revisit Conditions
- If a specific worker (e.g., Ingestion or ML Inference) requires independent horizontal scaling beyond the capabilities of the monolith deployment, it will be extracted into a standalone service.
