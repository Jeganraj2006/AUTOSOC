# Phase 9: Implementation Plan - Rule-Based Threat Detection

## Overview
This phase establishes the deterministic, rule-based threat detection layer of AutoSOC. The Detection Worker will subscribe to `security.events.enriched`, evaluate each event against a configured set of deterministic rules, and produce actionable alerts for analysts.

## Baseline Verification Results
- **Backend API**: Pytest test suite ran successfully (5 passed) locally.
- **Frontend App**: Vitest passed successfully; production build completed via Turbopack (8.8s).
- **Ingestion/Normalization Workers**: Schemas and endpoints verified intact.
- **Health**: PostgreSQL, Redis, Redpanda, and OpenSearch are structurally sound from Phase 8.

## Proposed Architecture
The Detection Worker will be implemented in Python under `workers/detection/`.

### 1. Schemas (`packages/event-schemas`)
- Add `DetectionResult` schema containing fields: `detection_id`, `rule_id`, `event_ids`, `severity`, `confidence`, `candidate_mitre_techniques`, `entities`, etc.

### 2. Detection Engine (`workers/detection`)
- **Consumer**: Asynchronous consumer pulling from `security.events.enriched`.
- **Registry**: Loads YAML-based rules from `workers/detection/rules`.
- **Evaluator**: Applies predicates.
  - **Field-Match/Multi-condition**: Simple exact or regex-based JSON field evaluations.
  - **Threshold**: Uses Redis to track occurrences (e.g., failed logins) with a sliding window (TTL). Triggers when the count exceeds a threshold.
  - **Stateful/Statistical**: Uses Redis to track observed behavior (e.g., previously seen ports/IPs) to identify "new" or "rare" observations.
  - **Sigma-Subset**: Supports a safe, read-only subset of Sigma YAML fields mapped to OCSF-inspired schema.
  - **IOC Matching**: Simple local list lookup.

### 3. State Management (Redis)
- Redis will maintain short-lived state:
  - `autosoc:detect:count:{rule_id}:{group_key}` -> integer counter
  - `autosoc:detect:suppress:{rule_id}:{group_key}` -> boolean lock

### 4. Alert Persistence & API (`apps/api`)
- Worker publishes `DetectionResult` to `security.alerts` Redpanda topic and uses SQLAlchemy to directly persist Alert metadata into PostgreSQL, leveraging the Phase 5 schema (`Alert` model).
- Implement `GET /api/v1/alerts`, `GET /api/v1/alerts/{id}`, and `PATCH /api/v1/alerts/{id}/status`.

### 5. SOC Frontend (`apps/web`)
- **Alerts List**: `/alerts` table with filtering by severity, status, time.
- **Alert Detail**: `/alerts/[id]` showing human-readable trigger reasoning, parsed entities, candidate MITRE, and raw evidence links.
- **Rules Admin**: `/rules` list showing registered detections.
- **Dashboard**: Wire up the "Active Alerts" widget.

## Excluded Features
- No Machine Learning or probabilistic models.
- No incident generation or correlation.
- No automatic containment / response workflows.
- No dynamic execution (`eval()`, shell injection).

## Verification Plan
1. Generate synthetic failed logins.
2. Ensure threshold rule matches and persists Alert.
3. Validate API returns it and Frontend displays it properly.
