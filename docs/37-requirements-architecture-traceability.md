# Requirements to Architecture Traceability

This document verifies that the architecture defined in Phase 2 satisfies the requirements established in Phase 1.

## Traceability Review

- **FR-AUTH-001 (OIDC/RBAC)**: Supported by `ADR-007` (Keycloak) and the Identity & Access Architecture (`27`).
- **FR-INGEST-001 (Log Ingestion)**: Supported by `ADR-006` (Redpanda) and the Event Lifecycle (`22`).
- **FR-PROC-001 (Normalization)**: Supported by `ADR-012` (OCSF schema) and the Component Architecture (`20`).
- **FR-DETECT-001 & FR-ML-001 (Hybrid Detection)**: Supported by `ADR-013` (Separation of Detection) and the Detection Worker component.
- **FR-INCIDENT-001 & FR-INCIDENT-002 (Correlation/Graph)**: Supported by the Incident Worker and `ADR-015` (Graph Storage in Postgres).
- **FR-AGENT-001 (Agentic AI)**: Supported by `ADR-009` (LangGraph) and the Agent Security Architecture (`31`).
- **FR-RESPONSE-001 (Human Approval)**: Strictly enforced by `ADR-010` and the Response Security Architecture (`32`).
- **NFR-SEC-001 (Agent Safety)**: Enforced via Tool Allowlisting and architectural isolation of the Response Worker (`31`, `32`).
- **NFR-PERF-001 (Throughput)**: Supported by the asynchronous, horizontally scalable worker architecture (`ADR-001`).
- **NFR-MAINT-002 (Portability)**: Supported by `ADR-011` (Docker Compose) and the Container Architecture (`19`).

## Gap Analysis & Resolution
During the architectural design, the following issues were identified and resolved:
1. **Unclear Vector Storage**: The MVP definition lacked a specific vector database. *Resolution*: Decided to use OpenSearch's built-in k-NN to reduce infrastructure bloat (`ADR-014`).
2. **Graph Storage Complexity**: Implementing a dedicated graph DB (Neo4j) for MITRE mapping violated the MVP simplicity constraint. *Resolution*: Decided to model the shallow attack graph relationally in PostgreSQL (`ADR-015`).
3. **Data Loss on Worker Crash**: Early conceptual models lacked retry logic. *Resolution*: Explicitly defined Dead-Letter Queues (DLQs) and Redpanda consumer offset management in the Event Lifecycle (`22`) and Resilience (`34`) docs.

**Conclusion**: The architecture fully supports all Phase 1 requirements, use cases, and success metrics. No architectural components exist without a corresponding requirement. All data categories have strict owners assigned.
