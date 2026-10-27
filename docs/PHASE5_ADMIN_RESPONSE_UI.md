# Phase 5.4 administration and response UI

## Completed interfaces

| Area | Existing integration | Result |
| --- | --- | --- |
| Response management | Incident list plus existing incident response proposal/review/approve/reject/dry-run hooks | Added an incident-scoped dedicated workspace, explicit confirmation before decisions and dry runs, mutation feedback, and validated-only success text. |
| Data sources | `GET/POST/PUT /data-sources` | Modernized page header, responsive inventory, loading/error/empty states, and preserved the validated create/edit dialog. Secret references remain write-only and are not displayed. |
| Detection rules | `GET /rules` | Modernized read-only configuration inventory with IDs, state, severity, category, ATT&CK metadata, and update time. No unsupported editing controls were added. |
| System health | `GET /health/live` | Displays reported API/dependency states, context, refresh, and no fabricated healthy defaults or performance metrics. |
| Audit activity | No audit query endpoint | Replaced a misleading placeholder with an explicit blocked state and the required safe API contract. |
| Account | `GET /auth/me`, Auth.js logout | Modernized session/role presentation and secure logout. Keycloak remains responsible for password/account management. |

## Response lifecycle boundary

The backend only exposes response recommendations per incident. It does not expose a global proposal queue, a read model for approvals/executions, or audit records. The new response page therefore selects an incident and uses the actual lifecycle panel. It does not invent approver, decision timestamp, execution record, or audit rows.

An approved dry run is labelled **Validated only — no external action performed**. No frontend change enables containment.

## Role behavior

- Viewer: monitoring remains read-only; no data-source management controls, response proposal, approval, or execution actions are enabled.
- SOC analyst: existing backend-authorized proposal/review capability remains available.
- Administrator: existing server-authorized source management and response approval/dry-run controls remain available.

Frontend visibility is a usability aid only; every mutation remains guarded by the existing backend permission dependencies.
