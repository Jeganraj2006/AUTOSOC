# Identity and Access Architecture

## Keycloak Realm Design
- **Realm**: `autosoc-realm`
- **Clients**: 
  - `autosoc-frontend` (Public client, PKCE for Next.js).
  - `autosoc-api` (Bearer-only client for FastAPI).

## Roles and Permissions
| Role | Permitted Domains | Prohibited Domains |
| :--- | :--- | :--- |
| **Administrator** | Data Sources, Rules, System Health | Direct Incident/Evidence Modification |
| **SOC Analyst** | Events, Alerts, Incidents, Agents, Responses | Rules, Data Sources, Audit Log Deletion |
| **Security Manager** | Reports, Read-Only Incidents | Response Approvals, Rule Modification |
| **Auditor** | Audit Logs, Read-Only Global | Any write operations (POST, PUT, DELETE) |

*(Note: System services/workers use Service Accounts with fine-grained API scopes rather than human roles).*

## Token Management
- **Access Tokens**: Short-lived (e.g., 5 minutes). Validated cryptographically by FastAPI on every request.
- **Refresh Tokens**: Longer-lived (e.g., 8 hours). Handled securely by the frontend (HttpOnly cookies if SSR, or secure local storage).
- **Logout**: Triggers token revocation at the Keycloak level and clears local state.

## Service-to-Service Authentication
- Background workers communicating with the FastAPI control plane use Keycloak **Service Accounts** utilizing the Client Credentials flow to obtain access tokens.

## Secrets Management
- Keys for external Threat Intel or Response Targets are stored in the database but encrypted at rest.
- Credentials for Keycloak, Postgres, and MinIO are injected via Environment Variables in Docker Compose (and via Kubernetes Secrets in production).

## Emergency Access
- The database administrator retains an emergency raw SQL account, restricted to localhost/internal network access, independent of Keycloak, for disaster recovery.
