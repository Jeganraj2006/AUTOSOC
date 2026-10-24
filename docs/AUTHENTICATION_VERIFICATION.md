# Authentication repair and verification

## Root cause

The sign-in route used a Keycloak issuer for a realm that had not been
provisioned. Auth.js therefore failed while loading OIDC discovery metadata.
After Keycloak was started and the realm was created, a second configuration
fault surfaced: the authorization request used `localhost` while the callback
code exchange was rewritten to `127.0.0.1` through `AUTH_URL`. Keycloak
correctly rejected that mismatched authorization-code redirect URI.

The local configuration uses `127.0.0.1` consistently for the Auth.js
application URL and callback, including the PKCE verifier cookie. Keycloak itself is reached on the loopback-only
`127.0.0.1:8080` listener, and both local app hosts are registered as client
redirect URLs and web origins.

## OIDC configuration

- Realm: `autosoc`
- Issuer: `http://127.0.0.1:8080/realms/autosoc`
- Client: `autosoc-frontend` (confidential)
- Flow: standard authorization-code flow with PKCE
- Canonical Auth.js callback: `http://127.0.0.1:3000/api/auth/callback/keycloak`
- Direct password grants: disabled
- Redirect URLs: `http://localhost:3000/*` and `http://127.0.0.1:3000/*`
- Web origins: `http://localhost:3000` and `http://127.0.0.1:3000`
- Backend validation: Keycloak issuer, signed RS256 JWKS tokens, audience
  `account`, expiration, issued-at and subject claims are required.

## Development identities

The bootstrap script generates 32-character, high-entropy passwords at runtime
and writes them only to the protected credential handoff outside the repository.
It does not print, embed, or commit passwords.

| Account | Keycloak realm role | Application role |
| --- | --- | --- |
| `autosoc_admin` | `administrator` | Administrator |
| `autosoc_analyst` | `soc_analyst` | Security Analyst |
| `autosoc_viewer` | `auditor` | Read-only Viewer |

## Verification performed

- Browser: Keycloak login form opened from the AutoSOC sign-in button; the
  administrator signed in and reached the dashboard.
- Browser: the dashboard made successful authenticated calls to `/auth/me` and
  `/events/dashboard/summary`; the latter requires `events:read`.
- OIDC: each account completed a fresh PKCE authorization-code exchange through
  the Keycloak login form protocol, with no password grant.
- Backend: each signed token was accepted by `/auth/me` and the protected
  dashboard summary endpoint; an invalid bearer token returned `401`.
- Authorization: `autosoc_admin` received `200` from `/auth/test-admin`, while
  the analyst and viewer correctly received `403`; both retained permitted
  read access to the dashboard summary.
- Logout: the AutoSOC and Keycloak sign-out flows returned to the AutoSOC login
  page before the successful final administrator login.
