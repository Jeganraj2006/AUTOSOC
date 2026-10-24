# Phase 2 security report

## Remediated findings

| Finding | Remediation | Verification |
| --- | --- | --- |
| JWT failures decoded unverified claims and created a privileged development identity | The validator now fails closed with 401. It requires a valid RS256 signature, issuer, audience, `exp`, `iat`, and `sub`. | Invalid JWKS and expired-token regression tests pass. |
| Public event ingestion, detection, dashboard, and search routes | Event routes now use explicit read, ingest, or detect permissions. | Missing-token event access test returns 401. |
| Public incident reads and mutations with the `system` actor | Incident reads and writes now require permissions; status transitions and notes receive the authenticated subject as the audit actor. | Missing-token and insufficient-role mutation tests pass. |
| Broad role checks and agent GET side effect | Alert, prediction, response, and agent routes use named permissions. Listing agent executions no longer creates or executes work. | Route review and backend suite pass. |
| A recommendation author could approve their own recommendation | Approval requires `responses:approve` and rejects the recommendation author. | Enforcement is present in the approval endpoint. |
| Frontend accepted dummy Keycloak credentials and called a nonexistent password endpoint | The Credentials provider was removed. NextAuth uses Keycloak authorization-code flow only and requires server-side configuration. | Web production build passes with supplied verification settings. |
| Embedded compose/bootstrap credentials | Compose requires local environment variables; Keycloak bootstrap reads required variables and disables direct password grants. | Compose configuration validates without defaults. |

## Authorization model

| Resource/action | Permission |
| --- | --- |
| Event search/dashboard/detail | `events:read` |
| Event CSV/packet/seed ingestion | `events:ingest` |
| Event anomaly detection | `events:detect` |
| Incident read | `incidents:read` |
| Incident status/note mutation | `incidents:update` |
| Agent execution read/run | `agents:read` / `agents:run` |
| Prediction read/recompute | `predictions:read` / `predictions:manage` |
| Response recommend/read/approve/execute/manage | Corresponding `responses:*` permission |

`administrator` has the complete permission set. `soc_analyst` can investigate and
recompute predictions but cannot ingest events or approve recommendations. `security_manager`
can approve and execute responses. `auditor` remains read-only.

## Deployment requirements

The local configuration uses Keycloak's standard `account` audience. A production Keycloak
realm should add an API audience mapper and set `KEYCLOAK_AUDIENCE` to that API audience;
the backend already verifies the configured audience rather than disabling the check.

The local deployment is HTTP and intended only for loopback development. Production requires
TLS termination, a protected Keycloak administrator account, secret management outside local
environment files, and an OpenSearch security configuration.
