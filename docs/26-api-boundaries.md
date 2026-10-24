# API Boundaries

All control plane API routes are prefixed with `/api/v1`.

| Domain | Main Operations | Required Roles | Sync/Async | Idempotency | Audit | Expected Failures |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Auth Context** | Verify token, get user profile | Any | Sync | Yes | No | 401 Unauthorized |
| **Data Sources** | Create, Delete, List | Admin | Sync | Create: No | Yes | 400 Validation Error |
| **Events (Search)**| Query logs with pagination | Analyst | Sync | Yes | Yes (Queries) | 503 OpenSearch Down |
| **Rules** | Upload YAML, Update threshold | Admin | Sync | Yes (Updates)| Yes | 400 Invalid Rule Syntax |
| **Alerts** | List, Update Status | Analyst | Sync | Yes | Yes | 404 Not Found |
| **Incidents** | List, Get Details, Merge | Analyst | Sync | Merge: No | Yes | 409 Conflict (Merging) |
| **MITRE / Graph** | Fetch Cytoscape nodes/edges | Analyst | Sync | Yes | No | 200 (Empty Graph) |
| **Predictions** | Fetch next-step predictions | Analyst | Sync | Yes | No | 404 Not Available |
| **Agents** | Trigger investigate, Get status | Analyst | Async | Trigger: No | Yes | 503 Worker Queue Full |
| **Responses** | Approve pending action | Analyst | Async | Yes (Approve)| Yes | 403 Forbidden (Not Admin) |
| **Reports** | Generate summary, Export PDF | Manager | Async | Yes | No | 504 Generation Timeout |
| **Auditing** | List logs, Search by user | Auditor | Sync | Yes | No (Meta) | 403 Forbidden |
| **Health** | `/health`, `/ready` | None | Sync | Yes | No | N/A |

## Common API Principles
- **Pagination**: All endpoints returning lists must support `limit` and `offset` (or cursor-based pagination).
- **Search**: Endpoints must support query parameters for basic filtering (e.g., `?severity=high&status=open`).
- **Failure Responses**: Errors follow a standard JSON schema: `{"error": "Type", "message": "Details", "trace_id": "123"}`.
