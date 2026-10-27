# Security architecture

Keycloak issues signed RS256 JWTs. The API retrieves JWKS and validates signature, issuer, audience, expiration, issued-at, and subject before mapping realm roles to permissions. The UI uses Auth.js Authorization Code + PKCE; access-token refresh failures are not returned as provider details. Administrator, analyst, and viewer are separately verified development roles.

Data-source provisioning requires `datasources:manage`; its key is created by `secrets.token_urlsafe(32)`, returned once, hashed with SHA-256, omitted from read schemas, and now revocable by an administrator. The ingestion service checks source enabled state and uses constant-time comparison. Audit reads recursively redact password, secret, token, authorization, cookie, and API-key fields.

Responses separate proposal, approval, and execution permissions. Approved dry runs produce only a `validated_only` record; no code path tested here executes containment. Unique execution idempotency keys protect duplicate requests. AI output is advisory and has no direct tool authority.

Local-development security limitations: Keycloak runs in `start-dev`; OpenSearch disables its security plugin; Redis/Redpanda/SeaweedFS traffic is not TLS-protected inside Compose; the browser session exposes the backend access token to client code for API calls; and persistent worker heartbeats/broker-lag metrics do not yet exist. These are release blockers for production, not hidden caveats.
