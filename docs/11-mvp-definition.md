# Minimum Viable Product (MVP) Definition

This document outlines the features required for the Minimum Viable Product (MVP), distinguishing them from extended project scope and optional future enhancements. The goal is to ensure a functional, demonstrable system can be completed within the academic timeframe.

## 1. MVP Scope
The following features MUST be implemented for the project to be considered a success:
- **Authentication and RBAC**: Basic Keycloak integration (Admin and Analyst roles).
- **Synthetic Event Ingestion**: A script/service to generate fake logs for testing.
- **Linux Syslog Ingestion**: Endpoint to receive standard syslogs.
- **Common Event Normalization**: Parsing IP addresses, timestamps, and basic categorization into an OCSF-inspired JSON format.
- **OpenSearch Log Search**: Backend indexing and frontend UI to search raw logs.
- **Basic SOC Dashboard**: UI showing recent alerts and system status.
- **Rule-Based Alerts**: Sigma-style matching for at least 5 known attack patterns.
- **Baseline Anomaly Detection**: A simple ML model (e.g., Isolation Forest via scikit-learn) to flag unusual traffic volume/patterns.
- **Incident Creation**: Grouping alerts by IP address over a 5-minute window.
- **MITRE ATT&CK Mapping**: Tagging alerts with MITRE tactics/techniques (static mapping).
- **Evidence-Based Incident Summary**: Basic LLM prompt to summarize the alerts in an incident.
- **Response Recommendation with Analyst Approval**: UI button to "Approve" a hardcoded response (e.g., block IP), which writes to an audit log but does not execute against real infrastructure.
- **Docker Compose Deployment**: The entire MVP can be spun up locally using `docker-compose up`.

## 2. Extended Project Scope (Targeted for Final Submission)
If the MVP is completed ahead of schedule, the following features will be implemented to fulfill the complete vision:
- Windows event-log, Network-flow, Kubernetes audit-log, and AWS CloudTrail ingestion.
- Dead-letter handling and automated retries in Redpanda.
- Advanced PyTorch neural networks for potential zero-day detection with high confidence scoring.
- Interactive attack-graph visualization using Cytoscape.js.
- Attack-progression prediction (likely next-technique prediction).
- Agentic AI RAG workflow (LangGraph autonomously querying OpenSearch).
- Management summaries and Risk assessment scoring.
- Dry-run response simulation API.
- Response rollback support.
- Production-style Kubernetes deployment configurations (Helm/Kustomize).
- CI/CD pipelines (GitHub Actions) with automated testing and security scanning (Semgrep, Trivy).
- Application monitoring with OpenTelemetry, Prometheus, and Grafana.
- Model experiment tracking using MLflow.

## 3. Optional Future Enhancements (Post-Project / Out of Scope)
These features are not required for the academic submission but represent future roadmap items:
- Direct API integrations with enterprise firewalls (e.g., Palo Alto, Cisco) for actual response execution.
- Ingestion of full PCAP network packet captures.
- Deep reinforcement learning for automated response playbook generation.
- Multi-tenancy support for Managed Security Service Providers (MSSPs).
- Cloud-native deployment on AWS EKS or Azure AKS.
