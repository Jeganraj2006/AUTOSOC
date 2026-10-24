# Data Ownership

To prevent state inconsistencies, AutoSOC enforces strict data ownership. Only one component is the authoritative "writer" for any given dataset, though others may read it.

| Data Category | System of Record | Searchable Copy | Owner Component | Sensitive Fields |
| :--- | :--- | :--- | :--- | :--- |
| **Users & Roles** | Keycloak (Primary), Postgres (Ref) | None | Auth Module | Passwords, Tokens |
| **Data Sources** | PostgreSQL | None | Source Mgmt | API Keys (Encrypted) |
| **Raw Events** | MinIO (Archive) | Redpanda (Transient)| Ingestion Worker | PII, IPs, Payloads |
| **Normalized Events**| OpenSearch | None | Processing Worker | IPs, Usernames |
| **Detection Rules** | PostgreSQL | None | Rule Mgmt | None |
| **Alerts & Incidents**| PostgreSQL | OpenSearch | Incident Worker | Victim Info |
| **Incident Evidence** | PostgreSQL | OpenSearch | Incident Worker | Log Excerpts |
| **MITRE Graphs** | PostgreSQL | None | Incident Worker | None |
| **ML Models** | MLflow / MinIO | None | ML Inference | None |
| **Agent Executions** | PostgreSQL | None | Agent Worker | Prompts |
| **Response Approvals**| PostgreSQL | None | Response Module | Approver ID |
| **Audit Logs** | PostgreSQL | None | Audit Module | Executed Commands |
| **Telemetry** | Prometheus | Grafana | Observability Stack | None |

## Data Management Principles
- **No Shared Mutable State**: The FastAPI API never writes directly to OpenSearch. The Processing Worker handles indexing.
- **Immutability Requirements**: `audit_logs` and `incident_evidence` tables are append-only. The application logic prohibits `UPDATE` or `DELETE` statements on these tables.
- **Cache Usage**: Redis is used exclusively for rate limiting and 1-second deduplication windows by the Processing Worker. It is NEVER the system of record.
- **Retention Expectations**: Raw events in Redpanda expire after 7 days. Normalized events in OpenSearch are kept for 30 days (configurable). PostgreSQL business state is kept indefinitely.
- **Backup Requirements**: PostgreSQL and MinIO require daily automated backups. OpenSearch snapshots are taken weekly.
