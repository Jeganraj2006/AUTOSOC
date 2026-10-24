# Resilience and Failure Handling

AutoSOC is designed to fail safely. The absence of advanced AI features will never prevent the core deterministic SOC capabilities from functioning.

## Infrastructure Failures

| Scenario | User-Visible Impact | Data-Loss Risk | Recovery / Fallback |
| :--- | :--- | :--- | :--- |
| **PostgreSQL down** | API fails (503). | None (Events buffer in Redpanda). | Restart DB. Workers auto-reconnect and process backlog. |
| **OpenSearch down** | Log search fails. RAG fails. | Low (Norm events buffer in RP). | Circuit breaker on Agent. UI shows "Search Unavailable". |
| **Redpanda down** | Ingestion fails (503). | High (for incoming streams). | API returns 503 so source systems retry sending. |
| **Redis down** | Rate limits fail open. | None (Ephemeral). | Restart Redis. Deduplication temporarily disabled. |
| **MinIO down** | Cannot download reports. | None. | MLflow uses cached models. |
| **Keycloak down** | Cannot login. | None. | Existing valid tokens continue to work until expiry. |

## AI / ML Failures

| Scenario | User-Visible Impact | Data-Loss Risk | Recovery / Fallback |
| :--- | :--- | :--- | :--- |
| **MLflow down** | None. | None. | Inference worker uses last downloaded model artifact. |
| **ML Inference fails**| Missing anomaly scores. | None. | Circuit breaker opens. Event marked as "Unscored". Rules still apply. |
| **Local LLM down** | Agent investigation fails. | None. | Agent task transitions to "Failed". Manual investigation required. |
| **Threat Intel down** | Enriched fields empty. | None. | Processing worker catches exception and proceeds without enrichment. |

## Processing Failures

| Scenario | Handling Strategy | Audit / Alerting |
| :--- | :--- | :--- |
| **Worker crash** | Docker/K8s restarts the container. Consumer group rebalances. Redpanda ensures un-acked messages are re-delivered. | Alert: High restart count. |
| **Corrupted event** | Pydantic validation throws Error. Event pushed to `security.events.failed` (DLQ). Processing continues. | Alert: DLQ size > 0. |
| **Duplicate event** | Redis deduplication drops it. If Redis fails, Redpanda delivers at-least-once. Incidents gracefully handle duplicate alerts. | N/A |
| **Processing timeout**| Worker drops event if normalization takes > 5s and routes to DLQ. | Alert: Processing latency. |
| **Queue backlog** | Horizontal pod autoscaling (K8s) spins up more workers based on lag metrics. | Alert: Lag > 60s. |
| **Partial update** | SQLAlchemy transactions ensure complete commits. If a crash happens mid-update, the DB rolls back. | N/A |
| **Response failure** | Response worker marks DB status as `ERROR`. | Audit log: "Execution Failed". |
