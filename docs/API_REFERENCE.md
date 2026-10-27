# API reference

The interactive OpenAPI document is available locally at `http://127.0.0.1:8000/api/v1/openapi.json` when the API is running. All SOC API routes require a valid Keycloak access token unless explicitly documented as health/version.

| Prefix | Purpose |
| --- | --- |
| `/api/v1/health` | liveness, readiness, version, and observed operational dependencies |
| `/api/v1/events`, `/alerts`, `/incidents` | paged security read models and incident operations |
| `/api/v1/data-sources` | Administrator source provisioning, update, and `POST /{id}/revoke` key revocation |
| `/api/v1/audit` | RBAC-protected, secret-redacted audit records |
| `/api/v1/incidents/{id}/responses`, `/responses` | proposal, approval/rejection, execution, global response reads |
| `/api/v1/incidents/{id}/agents` | investigation read/request endpoints |
| `/api/v1/incidents/{id}/predictions` | persisted prediction reads |

The ingestion service separately exposes `POST /api/v1/ingest/events` on port 8001. It requires `X-Source-Id` and `X-Api-Key`. A source key is returned only in the create response, is stored only as SHA-256, and can be irreversibly revoked. Never place it in a browser or repository.
