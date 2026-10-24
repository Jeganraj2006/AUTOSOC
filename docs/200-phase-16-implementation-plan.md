# Phase 16: Response Playbooks & Safe Containment - Implementation Plan

## Goal Description
Implement the Response framework enabling safe, human-approved response actions in the SOC. This phase introduces response recommendations, an approval workflow, a strict policy engine, and controlled execution supporting dry-run and simulation modes. It completely blocks unrestricted shell execution and production deployment to ensure maximum safety.

## User Review Required
> [!IMPORTANT]
> - **Execution Mode**: Production execution is disabled by default. All executed actions will be simulated or confined to strict mock/lab connectors (e.g. mock firewall for IP block, Keycloak dev realm for account disable). 
> - **No Shell Executor**: In compliance with the critical rules, there will be no generic shell/Bash/PowerShell executor. All playbooks will map strictly to typed, approved Python executor functions.
> - Please confirm these strict constraints meet your requirement before proceeding.

## Open Questions
1. Do you want the mock firewall (IP Blocking) to persist blocked IPs in a local SQLite file within the lab container, or just log to stdout for the MVP simulation?

## Proposed Changes

---

### Database Models

#### [NEW] [response_models.py](file:///d:/PROJECT%20WORKKKKKKKKKK/apps/api/src/autosoc_api/db/models/response.py)
- `ResponseRecommendation`: Captures the suggested action (manual or AI).
- `ResponseApproval`: Tracks the manual human approval state, reviewer, and expiration.
- `ResponseExecution`: Tracks the execution instance, idempotency key, verification, and rollback status.

#### [NEW] [response_schemas.py](file:///d:/PROJECT%20WORKKKKKKKKKK/apps/api/src/autosoc_api/schemas/response.py)
- Pydantic models for the response entities, ensuring strong validation of modes (`dry_run`, `simulation`, `analyst_approved_execution`).

---

### Backend API Endpoints

#### [NEW] [responses.py](file:///d:/PROJECT%20WORKKKKKKKKKK/apps/api/src/autosoc_api/api/v1/endpoints/responses.py)
- `POST /incidents/{incident_id}/responses` (Create recommendation)
- `GET /incidents/{incident_id}/responses` (List recommendations & history)
- `POST /responses/{id}/request-approval`
- `POST /responses/{id}/approve`
- `POST /responses/{id}/reject`
- `POST /responses/{id}/execute`
- `POST /response-executions/{id}/rollback`

#### [MODIFY] [permissions.py](file:///d:/PROJECT%20WORKKKKKKKKKK/apps/api/src/autosoc_api/auth/permissions.py)
- Add new RBAC permissions: `responses:read`, `responses:approve`, `responses:execute`.

---

### Response Worker Microservice

#### [NEW] [workers/response/pyproject.toml](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/response/pyproject.toml)
- Define `autosoc_response` worker dependencies (pydantic, redis, sqlalchemy).

#### [NEW] [workers/response/src/autosoc_response/policy/engine.py](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/response/src/autosoc_response/policy/engine.py)
- Implements the strict Policy Engine. Deny by default, environment guard, target scope validation.

#### [NEW] [workers/response/src/autosoc_response/playbooks/](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/response/src/autosoc_response/playbooks/)
- Registry logic to load and validate YAML playbooks from `rules/response-playbooks/`.

#### [NEW] [workers/response/src/autosoc_response/executors/](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/response/src/autosoc_response/executors/)
- Typed executors (e.g., `mock_firewall_executor.py`, `keycloak_disable_executor.py`, `simulation_executor.py`).

---

### Playbooks

#### [NEW] [rules/response-playbooks/](file:///d:/PROJECT%20WORKKKKKKKKKK/rules/response-playbooks/)
- `pb_001_increase_monitoring.yml`
- `pb_002_block_ip.yml`
- `pb_003_disable_test_account.yml`
- `pb_008_quarantine_test_file.yml`

---

### Frontend UI

#### [MODIFY] [page.tsx](file:///d:/PROJECT%20WORKKKKKKKKKK/apps/web/src/app/(soc)/incidents/[id]/page.tsx)
- Add "Response Actions" tab to the incident details page.

#### [NEW] [response-panel.tsx](file:///d:/PROJECT%20WORKKKKKKKKKK/apps/web/src/components/incidents/response-panel.tsx)
- Display the history of recommendations, dry-runs, approvals, and execution results. Support action buttons for approval/execution if authorized.

## Verification Plan

### Automated Tests
- Unit tests for the Policy Engine (verifying deny-by-default and environment guards).
- API integration tests for the full `Recommendation -> Approval -> Execution` flow.
- Target injection tests ensuring no shell escapes in executor payloads.

### Manual Verification
- **E2E Scenario**: Manually create a recommendation to Block an IP. View the dry run. Approve the request as a Security Manager. Trigger the execution and observe the simulated/lab mock firewall result in the UI. 
- Attempt to execute without approval to ensure the policy engine blocks it.
