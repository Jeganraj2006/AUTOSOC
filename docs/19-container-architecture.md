# Container Architecture

## C4 Container Diagram

```mermaid
C4Container
    title Container Architecture for AutoSOC Platform

    Person(analyst, "SOC Analyst", "Investigates incidents.")

    System_Boundary(autosoc, "AutoSOC Platform") {
        Container(frontend, "Next.js Frontend", "React/TypeScript", "Provides the interactive UI.")
        Container(api, "FastAPI Control Plane", "Python", "Provides REST APIs for the frontend and manages synchronous flows.")
        Container(workers, "Background Workers", "Python/Celery or asyncio", "Asynchronously processes events, runs ML, and orchestrates LangGraph.")
        
        ContainerDb(postgres, "PostgreSQL", "Relational DB", "Stores users, rules, alerts, incidents, and audit logs.")
        ContainerDb(opensearch, "OpenSearch", "Search Engine", "Stores normalized logs for fast full-text and vector search.")
        ContainerQueue(redpanda, "Redpanda", "Kafka-compatible", "Streams events between ingestion, processing, and workers.")
        ContainerDb(redis, "Redis", "Key-Value Store", "Caches UI state and handles rate-limiting / distributed locks.")
        ContainerDb(minio, "MinIO", "Object Storage", "Stores raw log archives and ML model artifacts.")
        
        Container(mlflow, "MLflow", "Python Tracking Server", "Manages model lifecycle and parameters.")
        Container(observability, "Observability Stack", "Otel/Prometheus/Grafana", "Collects metrics and traces.")
    }

    System_Ext(keycloak, "Keycloak", "IAM")
    System_Ext(ollama, "Ollama", "Local LLM")
    System_Ext(security_sources, "Log Sources", "External Syslog/API")

    Rel(analyst, frontend, "Uses", "HTTPS")
    Rel(frontend, keycloak, "Authenticates", "OIDC")
    Rel(frontend, api, "API calls", "HTTPS/JSON")
    
    Rel(security_sources, api, "Sends logs to ingestion endpoints", "HTTPS")
    Rel(api, redpanda, "Publishes raw events", "Kafka Protocol")
    
    Rel(workers, redpanda, "Consumes and Publishes events", "Kafka Protocol")
    Rel(workers, postgres, "Reads/Writes business state", "SQL/TCP")
    Rel(workers, opensearch, "Indexes and queries logs", "HTTPS/REST")
    Rel(workers, redis, "Uses for deduplication", "RESP/TCP")
    Rel(workers, ollama, "Sends prompts (Agentic AI)", "HTTPS/REST")
    Rel(workers, mlflow, "Fetches model artifacts", "HTTPS/REST")
    
    Rel(api, postgres, "Reads/Writes", "SQL/TCP")
    Rel(api, opensearch, "Searches logs", "HTTPS/REST")
    
    Rel(mlflow, minio, "Stores artifacts", "S3 API")
    Rel(api, observability, "Sends traces", "OTLP")
    Rel(workers, observability, "Sends traces", "OTLP")
```

## Container Descriptions

### Next.js Frontend
- **Responsibility**: Provides the user interface for all SOC roles. Renders Cytoscape graphs and ECharts.
- **Owned Data**: Client-side session state (transient).
- **Interfaces**: REST APIs (to FastAPI).
- **Dependencies**: Keycloak (Auth), FastAPI.
- **Scaling**: Horizontally via standard Node.js clustering.
- **Failure Impact**: UI goes down; backend ingestion and processing continue unaffected.
- **Security Boundary**: Validates user input before sending to backend.

### FastAPI Control Plane
- **Responsibility**: Handles synchronous API requests from the frontend, manages configuration, and provides ingestion webhooks.
- **Owned Data**: Ephemeral request context.
- **Interfaces**: REST API, OpenAPI docs.
- **Dependencies**: PostgreSQL, OpenSearch, Redpanda, Redis.
- **Scaling**: Horizontally using Uvicorn/Gunicorn workers.
- **Failure Impact**: UI cannot function; webhook ingestion fails.
- **Security Boundary**: Enforces RBAC on all endpoints; validates payloads via Pydantic.

### Background Workers (Modular)
- **Responsibility**: Executes asynchronous tasks: Normalization, Rule-detection, ML-inference, Correlation, Agentic AI, and Response execution.
- **Owned Data**: Process memory.
- **Interfaces**: Consumes from Redpanda; calls Ollama/MLflow.
- **Dependencies**: PostgreSQL, OpenSearch, Redpanda, Ollama, MLflow.
- **Scaling**: Horizontally scaled based on consumer group lag.
- **Failure Impact**: Processing backlog builds up in Redpanda; no data loss occurs.
- **Security Boundary**: Operates entirely within the private network; no direct public ingress.

### PostgreSQL
- **Responsibility**: System of record for structured business data.
- **Owned Data**: Users, Roles, Incidents, Approvals, Audit Logs.
- **Interfaces**: SQL.
- **Scaling**: Vertical scaling primarily; read replicas if necessary.
- **Failure Impact**: System halts (API fails, workers retry).

### OpenSearch
- **Responsibility**: Fast searching of massive log volumes.
- **Owned Data**: Normalized/Enriched security events, vectors for RAG.
- **Interfaces**: REST API.
- **Scaling**: Horizontal clustering.
- **Failure Impact**: Log search fails; RAG fails.

### Redpanda
- **Responsibility**: Decouples ingestion from processing via topic-based streaming.
- **Owned Data**: Buffered security events (Raw, Normalized, Alerts).
- **Interfaces**: Kafka Protocol.
- **Scaling**: Horizontal clustering (partitions).
- **Failure Impact**: Total ingestion failure.

### Redis
- **Responsibility**: Ephemeral state management.
- **Owned Data**: Rate-limits, short-term deduplication windows.
- **Interfaces**: RESP.
- **Scaling**: Clustered/Sentinel.
- **Failure Impact**: Deduplication might fail leading to duplicate alerts.

### MinIO
- **Responsibility**: S3-compatible object storage.
- **Owned Data**: Model artifacts, raw log archives.
- **Interfaces**: S3 API.
- **Scaling**: Horizontal clustering.
- **Failure Impact**: MLflow cannot load models; archiving fails.

### MLflow
- **Responsibility**: Tracks ML experiments and registers models.
- **Owned Data**: Model parameters, metrics.
- **Interfaces**: REST API.
- **Scaling**: Single instance usually sufficient for MVP.
- **Failure Impact**: New models cannot be registered; workers can still use cached models.
