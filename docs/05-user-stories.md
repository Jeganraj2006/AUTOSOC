# User Stories

## SOC Analyst
| Story ID | Description | Priority |
| :--- | :--- | :--- |
| **US-ANA-001** | As a SOC Analyst, I want to view a prioritized list of alerts so that I can focus on the most critical threats first. | High |
| **US-ANA-002** | As a SOC Analyst, I want to review AI-generated incident summaries so that I can understand the context of an attack without manually reading hundreds of logs. | High |
| **US-ANA-003** | As a SOC Analyst, I want to see an interactive attack graph mapped to MITRE ATT&CK so that I can visually understand the attacker's lateral movement. | Medium |
| **US-ANA-004** | As a SOC Analyst, I want to approve or reject AI-recommended response actions so that I maintain human control over potentially disruptive containment measures. | High |
| **US-ANA-005** | As a SOC Analyst, I want to add manual investigation notes to an incident so that my findings are preserved as evidence. | Medium |
| **US-ANA-006** | As a SOC Analyst, I want to simulate a response action before approving it so that I can verify it will not break critical business services. | High |

*Acceptance Criteria Example (US-ANA-004):*
- **Given** an incident with a recommended action "Block IP".
- **When** the Analyst clicks "Approve".
- **Then** the action executes, the status updates to "Executed", and an audit log is created.
- **Negative Scenario**: If the action fails downstream, the UI reflects "Execution Failed" and alerts the Analyst.

## Administrator
| Story ID | Description | Priority |
| :--- | :--- | :--- |
| **US-ADM-001** | As an Administrator, I want to configure new data sources so that the system can ingest logs from different parts of the network. | High |
| **US-ADM-002** | As an Administrator, I want to manage and update Sigma-style detection rules so that the system detects the latest known threats. | High |
| **US-ADM-003** | As an Administrator, I want to view system health metrics (queue lag, service uptime) via Grafana so that I can ensure the platform is stable. | Medium |
| **US-ADM-004** | As an Administrator, I want to assign roles (Analyst, Auditor) to users via Keycloak so that access control is strictly maintained. | High |

*Acceptance Criteria Example (US-ADM-002):*
- **Given** the Admin is on the Detection Rules page.
- **When** they upload a valid Sigma YAML file.
- **Then** the rule is parsed, saved to the database, and immediately applied to the processing pipeline.

## Security Manager
| Story ID | Description | Priority |
| :--- | :--- | :--- |
| **US-MGR-001** | As a Security Manager, I want to view a dashboard of incident trends over time so that I can report organizational risk to leadership. | Medium |
| **US-MGR-002** | As a Security Manager, I want to read LLM-generated management summaries of critical incidents so that I can understand business impact without technical jargon. | Medium |
| **US-MGR-003** | As a Security Manager, I want to review SOC performance metrics (Mean Time to Detect/Investigate) so that I can assess team efficiency. | Low |

## Auditor
| Story ID | Description | Priority |
| :--- | :--- | :--- |
| **US-AUD-001** | As an Auditor, I want to search and view the system audit logs so that I can verify who approved specific response actions. | High |
| **US-AUD-002** | As an Auditor, I want to export an incident report including all preserved evidence so that I have offline records for compliance purposes. | Medium |
| **US-AUD-003** | As an Auditor, I want read-only access to the entire platform so that I cannot accidentally modify or delete security data. | High |

## Automated Services (System Actors)
| Story ID | Description | Priority |
| :--- | :--- | :--- |
| **US-SYS-001** | As the Event-Ingestion Service, I want to publish incoming logs to a Kafka-compatible message queue so that processing is decoupled and scalable. | High |
| **US-SYS-002** | As the Detection Engine, I want to query the Redis cache for recent event state so that I can perform stateful, multi-event rule matching. | High |
| **US-SYS-003** | As the ML Inference Service, I want to score incoming normalized events for anomalies so that potential zero-day behaviors are flagged. | High |
| **US-SYS-004** | As the Correlation Engine, I want to group related alerts based on entity similarities and time windows so that Analysts aren't flooded with individual alerts. | High |
| **US-SYS-005** | As the Agent Workflow, I want to query OpenSearch for contextual logs so that I can build a comprehensive understanding of the incident via RAG. | High |
