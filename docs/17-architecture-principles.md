# Architecture Principles

The AutoSOC architecture adheres to the following core principles to ensure security, resilience, and maintainability:

## Core Principles

- **Security by design**: Security controls (authentication, validation) are built into the framework level (FastAPI/Pydantic) rather than bolted on as afterthoughts.
- **Least privilege**: Services and workers are granted only the database or API access they strictly require. The ML inference worker cannot execute response actions.
- **Zero-trust service communication**: All internal API calls require service-to-service authentication (e.g., via Keycloak client credentials).
- **Human approval for sensitive response actions**: The system structurally prohibits the execution of containment playbooks without an explicit cryptographic or database-backed approval record from a human Analyst.
- **Event-driven processing**: Heavy workloads (normalization, ML inference) are decoupled via Redpanda to prevent blocking the control plane API.
- **Clear module ownership**: Every domain (Alerts, Incidents, Agents) has a specific module in the API and specific worker(s).
- **Schema-first integration**: All data passing through the system conforms to strictly defined Pydantic schemas (OCSF-inspired) before processing.
- **Idempotent event processing**: Workers can safely replay events from Redpanda without duplicating alerts or incidents.
- **Explicit failure handling**: Every worker incorporates dead-letter queues (DLQs) and explicit retry mechanisms.
- **Auditability**: All state changes to critical entities (Users, Rules, Incidents, Responses) are immutably logged to an audit table.
- **Explainability**: ML models must output feature importance alongside anomaly scores; AI Agents must cite specific log IDs.
- **Observability**: Centralized metrics and distributed tracing (OpenTelemetry) are mandatory for all components.
- **Reproducibility**: Infrastructure is defined as code (Docker Compose / Kubernetes). ML models are tracked via MLflow.
- **Privacy by design**: PII masking is enforced at the normalization layer before data enters OpenSearch or the LLM context.
- **Safe degradation**: If the ML service or LLM fails, deterministic rule-based detection and the core UI remain functional.

## AI & Agent Specific Restrictions

- **Separation of detection and explanation**: ML/rules perform detection; LLMs perform summarization and explanation.
- **Separation of AI recommendations and response execution**: Agents can only write to a `recommendation` table; they cannot trigger the `execution` API directly.
- **No unrestricted agent access**: Agents operate in a restricted LangGraph workflow with explicitly defined, allowlisted tools.
- **No arbitrary shell execution**: No tools exist that allow the LLM to pass raw strings to a system shell (`subprocess.run(shell=True)` is prohibited globally).

## Data Integrity

- **No hidden dependencies**: All external API calls and database connections are explicitly injected.
- **No silent data loss**: Unparseable events are routed to a DLQ; they are never silently dropped.
