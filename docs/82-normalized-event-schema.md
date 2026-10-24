# Normalized Event Schema and Versioning

This document defines the canonical `NormalizedSecurityEvent` and `EnrichedSecurityEvent` structures.

## Schema Versioning Rules

- Every normalized event and enriched event MUST include a `schema_version` integer.
- The `schema_version` should be explicitly asserted during consumption and indexing.
- **Backward Compatibility:** Minor changes (adding optional fields) do not require a major version bump but should increment a documented minor revision if needed (though our schema uses integer `schema_version` which typically denotes major breaking changes).
- **Breaking Changes:** Renaming fields, removing fields, or changing data types requires incrementing `schema_version` and updating OpenSearch index mappings appropriately.
- Events with an unknown `schema_version` that exceeds the currently supported consumer version should be quarantined to the dead-letter queue (`security.events.failed`).

## Fields

See `packages/event-schemas/src/autosoc_schemas/events/normalized.py` for the definitive programmatic Pydantic definitions, which cover Identity, Time, Event Classification, Network, Identity, Host, Process, File, Authentication, Cloud, Kubernetes, and Provenance.
