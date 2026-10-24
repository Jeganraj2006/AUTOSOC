# Conceptual Event Schemas

*Note: These are conceptual representations, not programming language implementations.*

## RawSecurityEvent
- **Purpose**: Wraps incoming data directly from the source.
- **Required**: `source_id`, `received_timestamp`, `raw_payload` (string).
- **Correlation**: `trace_id` (OpenTelemetry).

## NormalizedSecurityEvent (OCSF-Inspired)
- **Purpose**: Canonical format for all log analysis.
- **Required**: `event_id`, `schema_version`, `timestamp`, `event_type` (Network, Auth, Process), `severity_id`.
- **Optional**: `src_ip`, `dst_ip`, `user_name`, `process_name`.
- **Sensitive Fields**: Passwords/tokens must be redacted before mapping to this schema.

## DetectionResult
- **Purpose**: Output when a normalized event matches a rule or anomaly model.
- **Required**: `detection_id`, `event_id`, `detection_type` (Rule | ML), `confidence_score` (0-100), `name` (e.g., "Potential Zero-Day Behavior").
- **Optional**: `mitre_tactics`, `mitre_techniques`.

## IncidentCreated
- **Purpose**: Emitted when alerts are grouped.
- **Required**: `incident_id`, `severity`, `status`, `created_at`.

## AgentTask
- **Purpose**: Instruction for LangGraph.
- **Required**: `task_id`, `incident_id`, `workflow_type` (e.g., "Full Investigation"), `priority`.

## AgentResult
- **Purpose**: Output of the LLM investigation.
- **Required**: `task_id`, `incident_id`, `technical_summary`, `recommended_actions` (Array).
- **Validation**: `recommended_actions` must strictly match the system's playbook allowlist.

## ResponseApproval
- **Purpose**: Cryptographic or immutable record of human authorization.
- **Required**: `approval_id`, `incident_id`, `action_name`, `approver_user_id`, `approved_at`, `target_entity`.

## AuditEvent
- **Purpose**: Immutable log of user and system actions.
- **Required**: `audit_id`, `timestamp`, `actor`, `action`, `resource`, `result_status`.
