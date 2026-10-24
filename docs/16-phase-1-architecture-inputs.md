# Phase 1 Architecture Inputs

## Confirmed Objectives
- Develop an Agentic AI-Driven Autonomous Security Operations Center for zero-day threat detection and attack progression prediction.

## MVP Capabilities
- Authentication and RBAC (FR-AUTH-001).
- Synthetic event and Linux Syslog ingestion (FR-INGEST-001, FR-INGEST-002).
- OCSF-inspired event normalization (FR-PROC-001).
- OpenSearch log search.
- Rule-based alerts (FR-DETECT-001) and baseline anomaly detection.
- Incident creation and MITRE mapping (FR-INCIDENT-001, FR-INCIDENT-002).
- Human-approved response recommendation (FR-RESPONSE-001).
- Local Docker Compose deployment (NFR-MAINT-002).

## Extended Capabilities
- Windows, k8s, CloudTrail ingestion.
- ML-based potential zero-day identification (FR-ML-001).
- Attack-progression prediction and graph visualization.
- Agentic RAG investigation workflows (FR-AGENT-001).
- K8s production deployment.

## User Roles
- Administrator, SOC Analyst, Security Manager, Auditor (Defined in `02-project-scope.md`).

## Functional Requirements Affecting Architecture
- **FR-AUTH-001**: Requires Keycloak integration in the API layer.
- **FR-INGEST-001**: Requires Redpanda and decoupling of ingestion from processing.
- **FR-PROC-001**: Requires dual writing to PostgreSQL and OpenSearch.
- **FR-AGENT-001**: Requires LangGraph orchestration and Ollama LLM integration.
- **FR-RESPONSE-001**: Requires a dry-run capability and asynchronous task orchestration for execution.

## Non-Functional Requirements Affecting Architecture
- **NFR-SEC-001**: Agent safety constraints require strict architectural separation of execution contexts.
- **NFR-PERF-001**: Target of 1,000 EPS requires horizontally scalable event processing workers.
- **NFR-REL-001**: Requires persistent event streaming (Redpanda) to survive database outages.
- **NFR-OBS-001**: Requires OpenTelemetry instrumentation across all FastAPI services.

## Security Constraints
- No unrestricted agent execution.
- Sensitive data masking required before LLM inference.
- Human approval mandatory for containment actions.

## Hardware and Performance Assumptions
- Deployed locally on a 4-core, 16GB RAM machine.
- Ollama uses a lightweight model (e.g., Llama 3 8B) fitting in available local GPU/CPU RAM.

## Major Project Risks
- **RSK-001** (Incompatible schemas): Handled via OCSF normalization worker.
- **RSK-009** (Hallucinations): Handled via strictly bounded RAG workflows in LangGraph.
- **RSK-013** (OpenSearch resource consumption): Addressed via strict data retention policies in the storage architecture.

## Unresolved Phase 1 Issues
- Specific PyTorch model architectures are deferred to Phase 10 implementation.
