# ADR-007: Keycloak for Identity Management

## Status
Accepted

## Context
AutoSOC requires robust authentication and Role-Based Access Control (RBAC) to differentiate between Administrators, Analysts, Managers, and Auditors. Managing users, passwords, and tokens natively within the application introduces significant security risks and distracts from core SOC features.

## Decision
We will use Keycloak as the Identity and Access Management (IAM) provider, utilizing OpenID Connect (OIDC) for authentication and authorization.

## Alternatives Considered
- **Custom JWT Auth via FastAPI**: Rejected due to the complexity of managing password resets, secure storage, token revocation, and complex role mappings safely.
- **Auth0 / Okta**: Rejected because the project must be fully deployable locally (air-gapped or academic environments) without relying on commercial SaaS providers.

## Positive Consequences
- Enterprise-grade security for user authentication out-of-the-box.
- Standardized OIDC flows make frontend and backend integration straightforward.
- Easy management of roles and groups via the Keycloak admin console.

## Negative Consequences
- Adds another heavyweight container to the local deployment footprint.
- Configuration of realms, clients, and scopes can be complex to automate.

## Security Implications
- Offloads credential management to a dedicated, battle-tested system, significantly reducing the risk of credential theft from the application database.

## Revisit Conditions
- N/A; Keycloak is an established standard for open-source identity management.
