# Observability Architecture

## Instrumentation
- **OpenTelemetry (OTel)**: All FastAPI services and background workers are instrumented with the OTel Python SDK. 
- **Prometheus**: Scrapes `/metrics` endpoints exposed by the OTel SDK to collect time-series data.
- **Grafana**: Provides the visualization layer for metrics and traces.

## Collected Data

### 1. Metrics (Prometheus)
- **Throughput & Lag**: Event ingestion rate (EPS), Redpanda queue lag per consumer group.
- **Latency**: Processing latency (Normalization), Detection latency (Rule evaluation), Inference latency (PyTorch execution), Agent latency (LLM generation time).
- **Health**: PostgreSQL connections, OpenSearch cluster green/yellow/red status, Redis memory usage, Worker memory/CPU usage, Keycloak availability.
- **Errors**: Agent tool failures, Response execution failures, HTTP 5xx rates.
- **AI Specific**: Model drift indicators (e.g., shifts in average anomaly scores over a 24h period).

### 2. Distributed Traces
- **Trace Identifiers**: An OTel `trace_id` is generated at the Ingestion API and propagated via Kafka headers through the Normalization, Detection, and Incident workers.
- **Correlation Identifiers**: `incident_id` and `event_id` are injected as spans tags to tie system performance directly to business entities.

### 3. Application Logs
- **Log Structure**: Structured JSON logging is enforced across all Python services (`{"timestamp", "level", "message", "trace_id", "module"}`).
- **Sensitive-Data Masking**: The Python logging formatter uses Regex to redact obvious secrets (e.g., `Bearer [A-Za-z0-9\-\.]+`) before writing to stdout.
- **Retention**: Application logs are kept for 7 days in the local deployment.

### 4. Security Audit Logs (CRITICAL SEPARATION)
- Security audit logs (tracking who approved a response, who altered a rule) are **strictly separated** from standard application stdout logs.
- Audit logs are written directly to the `audit_logs` table in PostgreSQL. They are immutable and retained indefinitely.

## Alerting Thresholds (Prometheus Alertmanager)
- **Critical**: PostgreSQL/Redpanda down, Ingestion queue lag > 5 minutes, HTTP 5xx > 1%.
- **Warning**: ML Inference latency > 2s, OpenSearch yellow status, High Agent tool failure rate (>10%).
