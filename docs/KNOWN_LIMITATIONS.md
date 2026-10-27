# Known limitations

- This release is for reproducible local development and academic demonstration, not production.
- OpenSearch security/TLS is disabled in the development Compose configuration.
- Keycloak uses `start-dev`; all infrastructure assumes a trusted local machine and loopback access where configured.
- Worker health is not durable: no persisted heartbeat or broker-lag metric proves ongoing consumption.
- The initial monolithic Playwright SOC-flow test timed out waiting for cold local Ollama inference. Durable retry later completed successfully; timing remains hardware-sensitive.
- A fresh Phase 6 monolithic Playwright pipeline run also timed out at its generic durable-result waiter, even though direct persistence checks later found its raw/normalized events, incident, prediction, and completed local-Ollama execution. It remains a failed E2E check until the exact waiter stage is reproduced and corrected.
- The older API-background LangGraph investigation path coexists with the verified durable agent worker and should be consolidated.
- No live threat-intelligence enrichment, SOC alert tuning/accuracy validation, external SOAR connector, production backup automation, HA, TLS termination, secret vault, or CI vulnerability gate is implemented.
- Redis-dependent deduplication and source rate limiting retain availability-oriented fail-open behavior if Redis is unavailable; this needs a product-level availability/security decision before production.
- Compose exposes ingestion worker development ports 8001–8003 and UDP 5140 beyond loopback; restrict them with host firewall rules if not needed.
