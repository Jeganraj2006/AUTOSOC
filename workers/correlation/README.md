# AutoSOC Correlation Worker

This worker consumes alerts from `security.alerts`, correlates them based on entity matching, temporal proximity, and rule chains, and generates/updates incidents in `security.incidents`.

## Responsibilities
- Rule-based evaluation of arriving alerts.
- Deduplication and Incident updating.
- Emits Incident status to Redpanda.
- Uses Redis for short-term active state tracking of candidate sequences.
