# Database architecture

PostgreSQL is migrated with Alembic from `apps/api/alembic/versions`. The currently present chain includes initial Phase 5 models, incident correlation, ATT&CK models, agent executions, response models, data-source fields, enum repairs, prediction and alert idempotency, agent telemetry, and Phase 5 read indexes.

Core durable relationships are: data source → raw/normalized event references → alert; incident ↔ alert/event link tables; incident → prediction and agent execution; incident → response recommendation → approval/execution; all protected actions → audit log. Response executions use a unique idempotency key. Detection and prediction migrations add durable logical-input protection. No migration deletes existing rows or Docker volumes.

Use `uv run --group dev alembic -c alembic.ini upgrade head` from `apps/api`. Back up PostgreSQL before any rollback or schema experiment; this release does not supply automatic production backup/restore automation.
