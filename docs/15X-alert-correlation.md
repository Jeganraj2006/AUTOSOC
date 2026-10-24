# Phase 12: Alert Correlation and Incident Management

## Overview
This phase implemented the incident management lifecycle for the AutoSOC project. We expanded on the existing rule-based detection engine and ML models to correlate isolated alerts into overarching incidents. This reduces analyst fatigue, provides context, and tracks investigation lifecycle events via strict audit logging.

## Core Implementations

### 1. Redis-backed State Management
- Utilized Redis for tracking rolling correlation windows.
- Keys are formatted as `corr:{rule_id}:{entity_id}` to bundle alerts associated with the same entity.
- Expiration is set natively on Redis keys based on rule configuration (e.g., `window_seconds: 3600`).

### 2. Correlation Engine
- Ingests `security.alerts` from Redpanda (generated in Phase 9/11).
- Processes alerts using correlation rules stored in YAML.
- Uses a threshold-based rule matcher. When thresholds are exceeded within a time window, an `Incident` is generated or appended to.

### 3. API & Backend Services
- Added `Incident` and `IncidentNote` tables to the database (via SQLAlchemy).
- Implemented `IncidentTransitionService` ensuring a strict Finite State Machine (FSM):
  `NEW` -> `TRIAGED` -> `INVESTIGATING` -> `RESOLVED` -> `CLOSED`.
- Every transition is immutably recorded via `AuditLog`.
- API endpoints `GET /api/v1/incidents` and `PATCH /api/v1/incidents/{id}/status` have been added.

### 4. Frontend Application
- New dashboard widgets display Incident metrics.
- Created `/incidents` data table allowing filtering by status and severity.
- Built an incident detail page `/incidents/[incidentId]` with tabs for timeline analysis, underlying alerts, and analyst notes.

## Security Controls
- **Immutability:** Audit Logs cannot be modified or deleted. Notes cannot be deleted once added.
- **Access Control:** Changing an incident's status requires specific roles (enforced by `PermissionGuard`).
- **Input Validation:** Pydantic models validate all incoming requests for Incident creation and state transitions.

## Current State
Phase 12 is fully operational. Alert ingestion flows completely from normalized events through the ML models, detection rules, and into actionable grouped incidents on the dashboard.
