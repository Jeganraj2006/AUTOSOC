# Worker reliability

## Implemented controls

The ingestion, normalization, detection, correlation, prediction, and agent workers now use bounded retry paths. Kafka consumers commit an offset only after durable success or a successfully published dead-letter record.

- Retry state is held in Redis by immutable `topic:partition:offset` identity and survives a worker restart.
- The default budget is five attempts with exponential backoff capped at 30 seconds.
- Retry exhaustion produces a `security.events.failed` record with a safe stage, offset, retry-count, and error summary.
- Ingestion reserves a source/payload hash atomically in Redis. It releases that reservation if archive or broker delivery is exhausted, so a legitimate source retry is not discarded.
- Detection uses deterministic UUIDv5 detection IDs and a database uniqueness constraint. Prediction input fingerprints and response-execution idempotency keys prevent replay duplicates.
- Correlation links only evidence that is not already attached and does not republish an unchanged incident.

## Live verification, 2026-10-25

A purpose-built Redis test recorded failure attempt 1, recreated the retry-state object, then observed attempt 2 and exhaustion. The test acknowledged the key after inspection. This verifies durable retry state, exponential delay, bounded attempts, and cleanup.

The agent worker also experienced an actual local-Ollama `ReadTimeout` during the synthetic run. Its execution record retained `retry_count: 1`, node timestamps, error telemetry, and subsequently completed successfully on retry.

## Limitations

The retry/DLQ paths have been exercised at the state-machine level and through the agent timeout. A destructive broker or database outage chaos test was not performed because it would disrupt the preserved local environment.
