# Phase 7 — Security Event Normalization and Enrichment Implementation Plan

## Goal Description
Build a reliable security-event normalization and enrichment pipeline. This phase transforms heterogeneous raw events from `security.events.raw` into a consistent `NormalizedSecurityEvent` canonical representation (OCSF-inspired), optionally adds business and threat context to create an `EnrichedSecurityEvent`, and indexes them securely into OpenSearch.

**Phase Boundary Constraints**: Detection rule evaluation, MITRE mapping, anomaly ML inference, and alert/incident generation are strictly **out of scope** for Phase 7.

## User Review Required

> [!WARNING]
> **Test Failures Noted in Baseline Verification**
> The backend `tests/test_health.py::test_root` currently fails because it expects `"Phase 3" in data["phase"]` but the API responds with `"Phase 5 - Core Backend"`. I will correct this to point to Phase 7 during the initial code fixes.
> Additionally, `workers/ingestion` fails `uv run pytest` due to path resolution for the local `autosoc-api` workspace dependency. I will update `pyproject.toml` to map to local paths if needed, or adjust the `pytest` runner context.

> [!IMPORTANT]
> **OpenSearch & Redpanda Lifecycle**
> Are there specific constraints regarding OpenSearch index settings (e.g. number of shards, replicas) for local development? I plan to use 1 shard and 0 replicas for local OpenSearch. Is that acceptable?

## Proposed Changes

---

### Shared Schemas (`packages/event-schemas/`)

#### [NEW] [normalized.py](file:///d:/PROJECT%20WORKKKKKKKKKK/packages/event-schemas/src/autosoc_schemas/events/normalized.py)
* Define the canonical `NormalizedSecurityEvent` and `EnrichedSecurityEvent` models based on the OCSF-inspired schema required.
* Ensure fields use proper Pydantic typing, validation, and serialization.
* Implement explicit schema versioning mechanisms.

---

### Normalization Worker (`workers/normalization/`)

#### [NEW] [pyproject.toml](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/normalization/pyproject.toml)
* Base configuration for the new worker.

#### [NEW] [main.py](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/normalization/src/autosoc_normalization/main.py)
* Application entry point for the normalization worker, handling initialization, metrics, and lifecycle.

#### [NEW] [consumer.py](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/normalization/src/autosoc_normalization/consumer.py)
* Subscribes to `security.events.raw` using `aiokafka`.
* Responsible for reliable offset tracking (acknowledgement only after successful index/DLQ delivery).

#### [NEW] [publisher.py](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/normalization/src/autosoc_normalization/publisher.py)
* Handles dispatch to `security.events.normalized`, `security.events.enriched`, and `security.events.failed`.

#### [NEW] [registry.py](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/normalization/src/autosoc_normalization/registry.py)
* Central registry for source-specific parsers. Associates `source_type` with specific parsing logic safely.

#### [NEW] [parsers/*](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/normalization/src/autosoc_normalization/parsers/)
* Base parser interface (`base.py`).
* Individual normalizers for `synthetic`, `http_json`, `linux_syslog`, `windows_event`, `network_flow`, `kubernetes_audit`, `aws_cloudtrail`.
* Implement strict UTC timestamp conversions, safe IP/Port validators, and sensitive field redaction masks.

#### [NEW] [enrichment/*](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/normalization/src/autosoc_normalization/enrichment/)
* Modular enrichers: Asset (via API/DB proxy), User, GeoIP (stub/local), IP Reputation (local test source), MITRE candidate tags.

#### [NEW] [storage/opensearch.py](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/normalization/src/autosoc_normalization/storage/opensearch.py)
* OpenSearch indexing client handling bulk writes, explicit templated mapping initialization, and timeouts.

---

### Backend API (`apps/api/`)

#### [MODIFY] [events.py](file:///d:/PROJECT%20WORKKKKKKKKKK/apps/api/src/autosoc_api/api/v1/endpoints/events.py)
* **NEW Endpoint:** `GET /api/v1/events` for read-only querying of events from OpenSearch with bounded, parameterized search rules. No raw Lucene DSL accepted.
* **NEW Endpoint:** `GET /api/v1/events/{event_id}` for individual event details.

#### [MODIFY] [test_health.py](file:///d:/PROJECT%20WORKKKKKKKKKK/apps/api/tests/test_health.py)
* Fix the broken Phase 3 assertion.

---

### Infrastructure and Scripts

#### [MODIFY] [provision-event-topics.py](file:///d:/PROJECT%20WORKKKKKKKKKK/scripts/provision-event-topics.py)
* Append `security.events.normalized` and `security.events.enriched` to the required topics configuration.

#### [MODIFY] [compose.yml](file:///d:/PROJECT%20WORKKKKKKKKKK/infrastructure/docker/compose.yml)
* Add `normalization-worker` service alongside the ingestion components.

---

## Verification Plan

### Automated Tests
* Execute the backend pytest suite to confirm API integrity and correct `test_health.py`.
* Build cross-source parser contract tests inside `workers/normalization/tests/` to guarantee parser safety (e.g., verifying safe redaction on credentials and preventing arbitrary execution).
* Perform a full pipeline integration test in CI covering: `Synthetic Event -> Ingestion Worker -> Kafka -> Normalization Worker -> Enrichment -> OpenSearch`.
* Validate DLQ flow for intentionally malformed JSON and out-of-bounds timestamps.

### Manual Verification
* Run `docker-compose up` completely with MinIO, Redpanda, Redis, PostgreSQL, and OpenSearch.
* Execute `scripts/generate-synthetic-events.py` and query the newly exposed `GET /api/v1/events` endpoint to verify the presence, structure, and enrichment of events.
