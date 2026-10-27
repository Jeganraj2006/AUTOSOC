# Service inventory

| Service | Role | Verification status |
|---|---|---|
| postgres | durable application data | healthy; migrations at `d13e4f5a6b7c` |
| keycloak | OIDC identity | running; realm discovery returned 200 |
| redpanda | message broker | healthy; worker consumer groups assigned partitions |
| redis | state/deduplication | healthy; ingestion duplicate replay was suppressed |
| minio (SeaweedFS) | S3 raw archive | healthy; authenticated SDK round trip and restart persistence passed |
| opensearch | event search | healthy; normalization template initialized |
| ingestion-worker | authenticated intake/archive/publish | healthy endpoint; six accepted synthetic events and one duplicate suppression |
| normalization-worker | normalize/enrich/publish | consuming raw topic and published enriched events; OpenSearch indexing has a strict-mapping defect |
| detection-worker | rule evaluation/alerts | consuming enriched topic; 22 rules loaded; four alerts persisted |
| correlation-worker | incidents/evidence/ATT&CK/audit | consuming alerts; four incidents and audit records persisted |
| prediction-worker | Markov prediction | consuming incidents; predictions persisted |
| agent-worker | optional agent graph | running; graph initialised successfully, but it does not consume incident messages or persist investigations |

Do not interpret a running container as complete functional verification; the rightmost column is authoritative.
