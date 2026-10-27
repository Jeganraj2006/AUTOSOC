# Project modules

| Module | Responsibility |
| --- | --- |
| `apps/web` | Authenticated SOC user interface and browser tests |
| `apps/api` | API routes, JWT validation, persistence, migrations, response approval and audit records |
| `packages/event-schemas` | Raw, normalized, detection, and failed-event contracts |
| `workers/ingestion` | Source-key verification, rate limiting, archive, deduplication, raw publish |
| `workers/normalization` | Parse and index normalized telemetry |
| `workers/detection` | Rule evaluation, alert persistence, retry/DLQ handling |
| `workers/correlation` | Alert grouping, incident/evidence/ATT&CK persistence |
| `workers/prediction` | Incident prediction consumption and persistence |
| `workers/agents` | Evidence-grounded local-Ollama investigation and durable retry/DLQ |
| `rules` and `.agents/rules` | Detection and correlation configurations |
| `scripts` | Local bootstrap, topic provisioning, Keycloak setup, development helpers |
