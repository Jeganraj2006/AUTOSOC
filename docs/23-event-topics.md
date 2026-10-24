# Redpanda Event Topics

AutoSOC uses a streamlined set of topics in Redpanda to manage the event lifecycle without unnecessary complexity.

| Topic Name | Purpose | Producer | Consumer | Partition Key | Retention | Dead Letter Topic |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `security.events.raw` | Buffers incoming raw logs before processing. | Ingestion API | Processing Worker | Source IP | 7 Days | `security.events.failed` |
| `security.events.normalized` | Parsed, OCSF-compliant events ready for detection. | Processing Worker | Detection Worker | Event ID | 24 Hours | `security.events.failed` |
| `security.events.failed` | DLQ for malformed or unparseable events. | All Workers | Alerting / Admin | None | 30 Days | None |
| `security.detections` | Output of Rule matches and ML anomalies. | Detection Worker | Incident Worker | Entity ID | 7 Days | None |
| `security.incidents.events`| Stream of incident updates for real-time UI websockets. | Incident Worker | FastAPI (UI) | Incident ID | 1 Hour | None |
| `security.agent.tasks` | Async queue for LangGraph agent executions. | API / Incident Worker | Agent Worker | Incident ID | 24 Hours | None |
| `security.response.tasks` | Queue for approved containment executions. | API | Response Worker | Incident ID | 24 Hours | None |

## Schema Versioning
- Message payloads use JSON. 
- A top-level `schema_version` field is mandatory (e.g., `"schema_version": "1.0"`). Consumers must validate this field and drop/DLQ unsupported versions.

## Sensitive Data Concerns
- `security.events.raw` contains unmasked data. Access to this topic is restricted strictly to the Processing Worker via Redpanda ACLs.
- `security.events.normalized` has sensitive fields masked (e.g., passwords redacted) before publication.

## Ordering Requirements
- Exact chronological ordering is not strictly required across partitions, but events for a specific entity (e.g., an IP address) should map to the same partition (using Partition Key) to aid in stateful correlation.
