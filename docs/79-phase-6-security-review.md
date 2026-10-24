# Phase 6 Security Review

## Findings

1. **Source Impersonation**: Prevented. Each HTTP ingestion request must supply `X-Api-Key`, which is validated against the securely hashed `api_key_hash` in the `DataSource` PostgreSQL record. `syslog_udp` is statically bound for the MVP (assumes internal trusted network forwarder).
2. **Credential Leakage**: The plaintext API key is only generated once via `secrets.token_urlsafe(32)` and immediately hashed using SHA-256 for storage. It is never logged or exposed in API responses.
3. **Payload Denial of Service (DoS)**: A hard limit of `MAX_PAYLOAD_SIZE = 512KB` is enforced *before* parsing the JSON body in FastAPI. Batch sizes are limited to `100` events per request.
4. **Log Injection & Cross-Source Spoofing**: The raw payload is treated strictly as data. The `pipeline.py` wraps it in a strongly-typed `RawSecurityEvent` envelope without interpreting the contents. The `source_id` is derived from the authenticated token, not the client payload, preventing cross-source spoofing.
5. **Topic Injection**: Topics are statically defined in configuration (`REDPANDA_RAW_TOPIC`, `REDPANDA_FAILED_TOPIC`). Clients cannot supply arbitrary topic names.
6. **Archive Path Traversal**: Object keys in MinIO are generated server-side using UTC timestamps, the authenticated `source_type`, and `source_id`. No client-supplied path is accepted.
7. **Silent Event Loss**: Handled via robust DLQ logic. MinIO timeout or Redpanda timeout triggers a `FailedSecurityEvent` publication to `security.events.failed` with `retryable=True` and returns a 503 to the client, ensuring the source forwarder will retry.
8. **Duplicate Suppression Abuse**: Bounded by a 1-hour TTL in Redis. Event hashes are combined with `source_id`, preventing cross-tenant hash collisions from falsely suppressing valid events.

## Conclusion
The Phase 6 Ingestion Pipeline meets the required security standards for an untrusted input boundary. Malicious payloads will be safely serialized and stored as strings. Semantic normalization and execution are strictly deferred.
