# Phase 5 Implementation Plan

## Baseline Verification
Before beginning Phase 5, the repository baseline was checked using `.\scripts\verify.ps1`.
- **Pre-existing Failures Recorded**: 
  - Backend: `ruff format --check .` reports unformatted files. `mypy` reports strict typing issues in `main.py` and `config.py`.
  - Frontend: `eslint` reports `any` types. `typecheck` missing. `pre-commit` binary missing from PATH.
  - Phase 4 Infrastructure: `compose.yml` and related Phase 4 local infrastructure files do not exist in this workspace checkout.
These pre-existing issues and missing infrastructure pieces will not be attributed to Phase 5 regressions.

## Database Integration Plan
- **ORM**: SQLAlchemy 2.0
- **Driver**: `asyncpg` (Asynchronous access pattern)
- **Migrations**: Alembic (async template)
- **Base Model**: UUID primary keys, `created_at` (UTC), `updated_at` (UTC).

## Models
- `DataSource` (metadata)
- `DetectionRuleMetadata`
- `Alert` (foundation)
- `Incident` (foundation)
- `AuditLog`
- `SystemSetting`

## Authentication Design
- OIDC Bearer JWTs provided by Keycloak.
- Backend retrieves and caches JWKS endpoint.
- Validates signature, audience, issuer, expiry.
- Extracts `sub`, `email`, and `realm_access.roles`.

## Authorization Design
- **Roles**: `administrator`, `soc_analyst`, `security_manager`, `auditor`.
- Centralized mapping to fine-grained permissions.
- `require_permission(perm)` dependency injected into FastAPI routes.
- Deny-by-default posture.

## Exclusions (Phase Boundary)
- No event ingestion pipelines.
- No Sigma rule execution.
- No real alert generation or correlation.
- No frontend authentication UI (unless minimal dev testing requires it).
- No production database credentials in source.
