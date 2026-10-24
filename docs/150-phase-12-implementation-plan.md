# Phase 12 Implementation Plan: Alert Correlation & Incident Management

This plan outlines the architecture, data models, APIs, frontend UI, and background worker for Phase 12 to group related alerts into actionable incidents.

## 1. Database Schema Updates
We will complete the Incident model and establish relationships with alerts and events in PostgreSQL.

### [MODIFY] `packages/database/src/autosoc_database/models/incident.py`
Add necessary fields to `Incident`:
- `risk_score` (float)
- `first_seen`, `last_seen` (timestamp)
- `alert_count`, `event_count` (int)
- `primary_entities` (JSON)
- `tags`, `candidate_mitre_references`, `correlation_rule_ids` (JSON arrays)
- `resolution_summary`, `closure_reason`, `false_positive_reason` (str)

### [NEW] `packages/database/src/autosoc_database/models/incident_alert.py`
Association model mapping `incidents` to `alerts`:
- `incident_id`
- `alert_id`
- `linked_at`
- `correlation_reason`
- `correlation_score`
- `correlation_rule_id`

### [NEW] `packages/database/src/autosoc_database/models/incident_event.py`
Association model mapping `incidents` to raw `events`:
- `incident_id`
- `event_id`
- `source_type`
- `evidence_role`
- `linked_at`

### [NEW] `packages/database/src/autosoc_database/models/incident_note.py`
- `incident_id`
- `author_id`
- `content`
- `created_at`

### [NEW] `packages/database/src/autosoc_database/models/incident_timeline.py`
- `incident_id`
- `event_type` (security_event, alert, correlation, assignment, status_change, note, system)
- `timestamp`
- `data` (JSON)

## 2. Shared Schemas Updates
### [MODIFY] `packages/event-schemas/src/autosoc_schemas/events/detection.py`
Ensure the schema is fully compatible with Correlation Worker logic.
### [NEW] `packages/event-schemas/src/autosoc_schemas/events/incident.py`
Create `IncidentCreated` and `IncidentUpdated` event schemas to be published to `security.incidents`.

## 3. Redpanda Topics Provisioning
### [MODIFY] `scripts/provision-event-topics.py`
Add `security.alerts` and `security.incidents` to the `REQUIRED_TOPICS`.

## 4. Correlation Worker (`workers/correlation`)
We will create a new worker service handling real-time alert correlation.

### Directory Structure
```text
workers/correlation/
├── pyproject.toml
├── src/
│   └── autosoc_correlation/
│       ├── main.py
│       ├── consumer.py (Consumes security.alerts)
│       ├── publisher.py (Publishes security.incidents)
│       ├── engine/ (Core correlation logic & state tracking)
│       ├── rules/ (YAML rule registry & parsing)
│       ├── state/ (Redis short-term state)
│       ├── scoring/ (Risk & correlation scoring)
│       └── incidents/ (PostgreSQL creation/updates)
```

### Correlation Logic
- **State Management**: Redis will hold active correlation candidates (e.g., entity-based buckets with TTLs) to deduplicate and aggregate incoming alerts within time windows.
- **Rules Engine**: Read YAML rules from `.agents/rules/correlation/`. Rules will specify `required_entities`, `time_window`, and `correlation_type`.
- **Incident Creation**: Creates a new Incident in PostgreSQL when a threshold is met.
- **Incident Updating**: Updates an existing active Incident (extends `last_seen`, recalculates risk) if an incoming alert matches its active correlation keys.
- **Idempotency**: Kafka offsets are only committed after the Postgres transaction successfully updates the incident state.

## 5. API Layer (`apps/api/src/autosoc_api/`)
Implement RESTful routes for the frontend.

### [NEW] `apps/api/src/autosoc_api/api/routes/incidents.py`
- `GET /api/v1/incidents` (List with filters/pagination)
- `GET /api/v1/incidents/{incident_id}`
- `PATCH /api/v1/incidents/{incident_id}` (Update severity, etc.)
- `POST /api/v1/incidents/{incident_id}/assign`
- `POST /api/v1/incidents/{incident_id}/status`
- `POST /api/v1/incidents/{incident_id}/notes`
- `GET /api/v1/incidents/{incident_id}/timeline`
- `GET /api/v1/incidents/{incident_id}/alerts`
- `GET /api/v1/incidents/{incident_id}/evidence`

## 6. Frontend UI (`apps/web/src/app/(soc)/incidents`)
### [NEW] `/incidents`
Incident List View using standard data tables with sorting, filtering, and pagination.
### [NEW] `/incidents/[incidentId]`
Detailed investigation view:
- **Overview**: Severity, risk score, status, assignment.
- **Timeline**: Chronological sequence of alerts, events, notes, and state changes.
- **Alerts & Evidence**: Lists linked alerts and events.
- **Analyst Activity**: UI for adding notes, changing status, or assigning ownership.
- **Actions**: Transition statuses (e.g., `investigating`, `resolved`, `closed`, `false_positive`).

## 7. Security and RBAC
- Validate status transitions against a strict state machine inside the API (`services/incident_transition.py`).
- Notes will be rendered purely as plain text (no Markdown/HTML parsing in UI) to prevent XSS.
- Audit logs recorded for every status change, assignment, and note creation.
- Strict API permission enforcement for `SOC Analyst` vs `Security Manager`.

> [!IMPORTANT]
> User Review Required: Please review the plan above. If approved, I will implement the Correlation Worker, Database/API updates, and the Frontend UI.
> 
> *Note on Baseline:* I verified the repository. There are existing UI linting errors (e.g., `any` types in `apps/web`), which are noted and will be fixed when touching those files, but I will primarily focus on Phase 12 requirements.
