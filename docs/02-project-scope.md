# Project Scope

## 1. Introduction
This document defines the boundaries of the AutoSOC project. It outlines the specific capabilities that will be implemented (in-scope), the capabilities explicitly excluded from the project (out-of-scope), and the environmental constraints and assumptions under which the system will be developed.

## 2. In-Scope Capabilities
The project will implement the following core capabilities:
1. User authentication and role-based access control (OIDC via Keycloak).
2. Security data-source registration and system health monitoring.
3. Synthetic security-event generation for academic demonstrations.
4. Ingestion of logs: Linux Syslog, Windows event-log samples, Network-flow, Kubernetes audit-logs, and AWS CloudTrail.
5. Batch and streaming event processing (Redpanda).
6. Event validation, deduplication, dead-letter handling, and retries.
7. OCSF-inspired security-event normalization and enrichment.
8. OpenSearch-based log search capabilities.
9. Rule-based threat detection (Sigma-style rules) and Indicator-of-Compromise (IoC) matching.
10. Machine-learning attack classification and behavior-based anomaly detection (identifying potential zero-day behaviors).
11. Detection confidence scoring and explainability.
12. Alert generation, prioritization, and correlation into incidents.
13. Incident creation, management, evidence preservation, and timeline generation.
14. MITRE ATT&CK tactic and technique mapping with interactive attack-graph visualization (Cytoscape.js).
15. Attack-progression prediction (likely next-technique prediction).
16. Agentic AI-based incident investigation with threat-intelligence enrichment and RAG.
17. Risk assessment calculation.
18. LLM-generated technical incident summaries and management summaries.
19. Controlled response recommendations with dry-run response simulation.
20. Analyst approval/rejection workflows for responses, including rollback support.
21. Complete audit logging of all system and user actions.
22. Real-time SOC dashboard, security reports, and exports.
23. Application and infrastructure monitoring (OpenTelemetry, Prometheus, Grafana).
24. Model experiment tracking (MLflow) and model-drift monitoring.
25. CI/CD, automated testing, and security scanning (GitHub Actions, Pytest, Semgrep, Trivy).
26. Deployments: Docker Compose (local) and production-style Kubernetes.

## 3. Out-of-Scope Capabilities
The following are explicitly excluded from the initial project scope to maintain safety and academic focus:
- Unrestricted autonomous containment actions.
- Direct execution of arbitrary shell commands by AI agents.
- Use of production cloud credentials or live organizational data without authorization.
- Deployment against real organizations without explicit authorization.
- Development of malware, destructive exploit code, or weaponized payloads.
- Automatic classification of every anomaly as a confirmed zero-day attack (anomalies will be flagged as "potential zero-day behavior").
- Fully autonomous disabling of user accounts or production hosts without human approval.
- Unrestricted access by the LLM to underlying databases, terminals, or infrastructure.
- Replacement of deterministic detection logic entirely with LLM decisions.
- Direct merging of incompatible public dataset columns without careful transformation.

## 4. Intended Users
- **Administrator**: Manages the platform's configuration, rules, users, and health.
- **SOC Analyst**: The primary daily user investigating incidents and approving responses.
- **Security Manager**: Views high-level metrics and trends.
- **Auditor**: Reviews actions and logs read-only for compliance.

## 5. Operating Environment
- **Development**: Local environments using Docker Compose, Python 3.11+, and Node.js.
- **Production/Simulation**: Kubernetes clusters (e.g., Minikube, K3s, or managed cloud K8s) demonstrating a production-style architecture.
- **AI Environment**: Local LLM serving via Ollama for privacy, utilizing machine learning models trained via PyTorch/scikit-learn.

## 6. Constraints
- The system must rely on local LLM serving (Ollama) initially to prevent sensitive data leakage to third-party APIs.
- The project timeline is limited to a final-year academic schedule.
- Hardware limitations for training ML models; training must be feasible on accessible consumer GPUs or standard academic cloud resources.
- Response actions must be simulated or executed against synthetic/mocked infrastructure unless in a safely isolated lab.

## 7. Dependencies
- **Data Availability**: Availability of high-quality, labeled public datasets for training ML models.
- **Infrastructure Services**: Reliable operation of Keycloak, PostgreSQL, OpenSearch, Redpanda, and Redis.
- **Framework Compatibility**: Compatibility between FastAPI, SQLAlchemy, LangGraph, and other Python libraries.
- **Security Integration**: Continued availability of the MITRE ATT&CK framework data.

## 8. Expected Academic Contribution and Industry Relevance
This project bridges the gap between academic machine learning for intrusion detection and applied, industry-standard SOC engineering. It provides a blueprint for integrating Agentic AI securely into incident response workflows, ensuring that AI acts as an accelerator rather than a liability, enforcing the necessity of human-in-the-loop for high-risk actions.

## 9. Project Limitations
- The accuracy of the attack-progression prediction is heavily reliant on the training data quality.
- The system does not actively reverse-engineer malware or perform dynamic sandboxing of unknown binaries.
- The response simulation is limited to predefined playbooks and mock APIs.
