# System architecture

```mermaid
flowchart LR
  U["SOC users"] --> W["Next.js web :3000"]
  W --> K["Keycloak OIDC :8080"]
  W --> A["FastAPI :8000"]
  S["Telemetry source + one-time API key"] --> I["Ingestion worker :8001"]
  I --> O["SeaweedFS S3 :9000"]
  I --> R["Redpanda :19092"]
  R --> N["Normalization"] --> OS["OpenSearch :9200"]
  R --> D["Detection"] --> P["PostgreSQL :5433"]
  D --> C["Correlation"] --> P
  C --> PR["Prediction"] --> P
  C --> AG["Agent worker"] --> L["Local Ollama"]
  AG --> P
  D --> X["Redis retry/DLQ state"]
```

The API owns relational reads, RBAC-protected changes, audit records, and response approval/execution. Workers own streaming transforms. PostgreSQL is the durable record of alerts, incidents, predictions, investigations, response lifecycle, and audit history. SeaweedFS stores raw source objects; OpenSearch stores normalized event documents. All Compose ports are loopback-bound except worker development ports 8001–8003 and UDP 5140, which are documented as local-development exposure.
