# Event Lifecycle

The lifecycle describes a security event from generation to response execution.

```mermaid
sequenceDiagram
    participant Source as Security Source
    participant API as Ingestion API
    participant RP as Redpanda
    participant Proc as Proc Worker
    participant OS as OpenSearch
    participant Det as Det Worker
    participant Inc as Inc Worker
    participant PG as PostgreSQL
    participant Agent as Agent Worker

    Source->>API: 1. Send Raw Event
    API->>RP: 2. Publish (security.events.raw)
    RP->>Proc: 3. Consume Raw
    Proc->>Proc: 4. Normalize (OCSF)
    Proc->>OS: 5. Index Normalized Event
    Proc->>RP: 6. Publish (security.events.normalized)
    RP->>Det: 7. Consume Normalized
    Det->>Det: 8. Rule Match & ML Inference
    Det->>RP: 9. Publish (security.detections) if match
    RP->>Inc: 10. Consume Detection
    Inc->>PG: 11. Create/Update Alert & Incident
    Inc->>Agent: 12. Trigger AI (if High Severity)
    Agent->>OS: 13. Query Logs (RAG)
    Agent->>PG: 14. Save Summary & Recommendation
```

## Step Details

1. **Raw Event**:
   - **Input**: Unstructured JSON/Syslog.
   - **Validation**: Payload size limits.
2. **Publish Raw**:
   - **Idempotency**: N/A at ingestion.
   - **Failure**: Return HTTP 400 (Bad Request) or 503 (Unavailable).
3. **Normalize**:
   - **Schema**: Map to `NormalizedSecurityEvent`.
   - **Failure**: Route unparseable events to `security.events.failed` (DLQ).
4. **Index to OpenSearch**:
   - **Retry**: Exponential backoff.
5. **Detection (Rules/ML)**:
   - **Input**: `NormalizedSecurityEvent`.
   - **Output**: `DetectionResult`.
   - **Metrics**: Inference latency, Rule evaluation time.
6. **Incident Creation**:
   - **Input**: `DetectionResult`.
   - **Correlation**: Time window + shared entity (IP/User).
7. **Agent Investigation**:
   - **Input**: Incident ID.
   - **Failure**: Timeout after 60 seconds; log partial results.
8. **Response Approval**:
   - **Audit**: Log Analyst ID, timestamp, and approved action payload.
9. **Trace Propagation**:
   - OpenTelemetry Trace IDs are passed in Kafka headers across all steps to link ingestion to incident creation.
