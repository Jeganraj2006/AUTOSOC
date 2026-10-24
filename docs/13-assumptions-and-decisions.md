# Assumptions and Decisions

During Phase 1 (Requirements and Project Planning), the following assumptions and architectural decisions were made to resolve minor ambiguities and guide the project's scope:

## Key Assumptions

1. **Academic Environment Focus**: It is assumed that the primary deployment environment for this project is a local development machine or an academic lab server. Therefore, enterprise-grade high availability (e.g., multi-region clustering) is not required for the MVP.
2. **LLM Hardware Capabilities**: It is assumed that the local hardware has sufficient resources (CPU/RAM/GPU) to run Ollama and serve a 7B or 8B parameter model (e.g., Llama 3) with an acceptable context window for RAG operations.
3. **Dataset Availability**: It is assumed that high-quality public cybersecurity datasets (e.g., CIC-IDS, CSE-CIC-IDS2018, or BOTS) are available and can be mapped to the OCSF schema for training the ML models.
4. **Analyst Availability**: It is assumed that the system operates under a "human-in-the-loop" paradigm where a SOC Analyst is available to review and approve critical containment actions during standard operating hours.
5. **No Malicious Insider**: The threat model assumes that authenticated SOC Analysts are not malicious insiders attempting to sabotage the platform (though actions are audited regardless).

## Key Architectural Decisions

1. **OpenSearch over Elasticsearch**: OpenSearch was selected due to its open-source licensing model and robust integration with modern data pipelines, avoiding the licensing complexities of recent Elasticsearch versions.
2. **Redpanda over Kafka**: Redpanda was chosen as the event streaming platform because it is Kafka API-compatible but lighter weight and easier to deploy in a local Docker Compose environment (it removes the need for ZooKeeper).
3. **Local LLM serving**: The decision to use Ollama locally instead of OpenAI/Anthropic APIs was made to strictly enforce data privacy and prevent sensitive log data from leaving the academic environment.
4. **Synthetic Data First**: The MVP will utilize a synthetic event generator before integrating real-world datasets. This decision ensures that the data pipeline, detection engine, and UI can be developed and tested simultaneously without waiting for data preprocessing tasks to complete.
5. **Simulated Response Actions**: Rather than building complex integrations with enterprise firewalls (which may be unavailable), the response engine will rely on a "dry-run simulation" API that mocks the execution of playbooks to demonstrate the capability safely.

## Phase 2 Architectural Decisions (ADRs)
During Phase 2, major architectural decisions were formalized in Architecture Decision Records (ADRs). Please see the `docs/adr/` directory for full context:
- **ADR-001**: Modular Monolith with Background Workers.
- **ADR-002**: FastAPI for Control-Plane Backend.
- **ADR-003**: Next.js for Frontend.
- **ADR-004**: PostgreSQL as Authoritative Database.
- **ADR-005**: OpenSearch for Security-Event Search.
- **ADR-006**: Redpanda for Event Streaming.
- **ADR-007**: Keycloak for Identity Management.
- **ADR-008**: MLflow for Model Lifecycle.
- **ADR-009**: LangGraph for Agent Workflows.
- **ADR-010**: Human Approval for Response Execution.
- **ADR-011**: Docker Compose Before Kubernetes.
- **ADR-012**: OCSF-Inspired Canonical Event Schema.
- **ADR-013**: Separate Detection and LLM Responsibilities.
- **ADR-014**: Vector Storage Approach for RAG (OpenSearch k-NN).
- **ADR-015**: Initial Graph Storage Strategy (PostgreSQL Relational).
