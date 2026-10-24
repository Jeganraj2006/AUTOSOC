# Phase 13 Implementation Plan

## 1. Goal Description
Phase 13 integrates the MITRE ATT&CK framework and an Interactive Attack Graph into AutoSOC.

## 2. MITRE Data Acquisition Strategy
- Source: MITRE CTI official GitHub repository (`https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json`).
- Format: STIX 2.1 JSON.
- Mechanism: A Python script (`scripts/mitre/fetch_attack_data.py`) will download the bundle via HTTPS, calculate its SHA-256 hash, and store it locally in `data/mitre/manifests/enterprise-attack.json`. No arbitrary code execution.
- Updates: Administrator triggered; safe and idempotent database upserts.

## 3. Local Storage Strategy
- Backend: PostgreSQL using SQLAlchemy.
- Models: `AttackTactic`, `AttackTechnique`, `AttackRelationship`.
- Information Retained: `id`, `name`, `description`, `external_id`, `version`, `revoked`, `x_mitre_platforms`.

## 4. Mapping Architecture
- Model: `IncidentAttackMapping` maps an `Incident` to an `AttackTechnique`.
- Source tracking: Tracks how the mapping originated (e.g., `detection_rule`, `analyst`).
- Mappings MUST reference specific `Evidence` (alerts or events).

## 5. Automated vs Analyst-Confirmed Mapping
- Statuses: `candidate`, `supported`, `analyst_confirmed`, `rejected`.
- Candidate: Extracted from ML or weak rules.
- Supported: Extracted from deterministic rules with high confidence.
- Analyst Confirmed: SOC analyst explicit action.

## 6. Confidence & Evidence Design
- Confidence is a score derived from rule quality, evidence count, and normalization status.
- Mappings require valid external IDs (e.g., `T1110`).

## 7. Attack Graph Data Model
- Nodes: `IncidentGraphNode` (Incident, Alert, Event, User, Host, IP, Process, File, Technique).
- Edges: `IncidentGraphEdge` (`logged_into`, `connected_to`, `executed`, `mapped_to`, `associated_with`).
- Edge Creation: Only created when factual evidence links two entities.

## 8. Graph Persistence
- Store nodes and edges in PostgreSQL (`IncidentGraphNode`, `IncidentGraphEdge`).
- Adheres to Phase 2 ADR prohibiting a dedicated Graph DB like Neo4j unless necessary.

## 9. Graph APIs
- `GET /api/v1/incidents/{incident_id}/graph`: Returns paginated/limited nodes and edges.
- `GET /api/v1/incidents/{incident_id}/graph/nodes/{node_id}`: Deep dive into a node's evidence.

## 10. Frontend Architecture
- Library: `cytoscape` and `react-cytoscapejs`.
- Features: Interactive visualization, filtering by entity type, timeline slider, drawer for node details.

## 11. Security and Phase 14 Exclusions
- Security: Graph API checks user authorization to the underlying incident. Labels sanitized for XSS.
- Exclusions: No attack progression prediction, next-technique probabilities, or Agentic response (deferred to Phase 14).
