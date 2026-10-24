# Requirements Traceability Matrix

This matrix maps Project Objectives (Capabilities) to Functional Requirements (FR), Non-Functional Requirements (NFR), Use Cases (UC), Epics, and Test Categories.

| Project Capability | FR ID | NFR ID | Use Case | Epic | Test Category |
| :--- | :--- | :--- | :--- | :--- | :--- |
| User authentication and RBAC | FR-AUTH-001 | NFR-SEC-003 | UC-001 | Epic 5 | Unit, E2E |
| Data-source registration | FR-INGEST-001 | NFR-MAINT-003 | UC-002 | Epic 6 | Unit |
| Synthetic event generation | FR-INGEST-002 | NFR-PERF-001 | UC-002 | Epic 6 | Unit, Performance |
| Event ingestion (Syslog, Win, etc.) | FR-INGEST-001 | NFR-PERF-001, NFR-REL-001 | UC-003 | Epic 6 | Integration, Performance |
| Event validation & deduplication | FR-PROC-001 | NFR-PERF-001 | UC-004 | Epic 7 | Unit |
| OCSF normalization | FR-PROC-001 | - | UC-004 | Epic 7 | Unit |
| OpenSearch log search | - | NFR-PERF-003 | UC-005 | Epic 7, Epic 8 | Integration, E2E |
| Rule-based threat detection | FR-DETECT-001 | - | UC-006 | Epic 9 | Unit, Integration |
| ML-based anomaly detection | FR-ML-001 | NFR-AI-001, NFR-AI-002 | UC-007 | Epic 10, Epic 11 | ML Eval, Integration |
| Potential zero-day identification | FR-ML-001 | NFR-SEC-001 | UC-008 | Epic 11 | Integration |
| Alert correlation & Incident Creation | FR-INCIDENT-001 | NFR-PERF-002 | UC-010, UC-011 | Epic 12 | Unit, Integration |
| MITRE ATT&CK mapping & Graph | FR-INCIDENT-002 | - | UC-012, UC-013 | Epic 13 | E2E (UI) |
| Attack-progression prediction | FR-AGENT-001 | NFR-AI-001 | UC-014 | Epic 14 | ML Eval, Integration |
| Agentic AI investigation & RAG | FR-AGENT-001 | NFR-SEC-001, NFR-SEC-002 | UC-015 | Epic 15 | Integration, E2E |
| LLM incident/management summaries | FR-AGENT-001 | NFR-SEC-002 | UC-015, UC-020 | Epic 15 | Integration |
| Controlled response & dry-run | FR-RESPONSE-001 | NFR-SEC-001 | UC-017, UC-019 | Epic 16 | Unit, E2E |
| Analyst approval & rollback | FR-RESPONSE-001, FR-RESPONSE-002 | NFR-SEC-003 | UC-018 | Epic 16 | E2E, Security |
| Complete audit logging | FR-REPORT-001 | NFR-SEC-003 | UC-020 | Epic 5, Epic 16 | Integration, Security |
| SOC dashboard & Monitoring | FR-REPORT-001 | NFR-PERF-002, NFR-OBS-001 | UC-005, UC-009 | Epic 8, Epic 17 | E2E |
| CI/CD & Security Scanning | - | NFR-MAINT-001 | - | Epic 3 | CI Pipeline |
| Docker & K8s Deployment | - | NFR-MAINT-002 | - | Epic 4, Epic 17 | Deployment |

*Note: For the tracing of these requirements to specific architectural components, please see [Requirements to Architecture Traceability](37-requirements-architecture-traceability.md).*
