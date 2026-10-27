# Persisted synthetic pipeline test

Scenario: an isolated `SYNTHETIC` source submitted five authentication failures and one subsequent administrator login from `198.51.100.77` to `10.0.0.12`. The exact replay of the fifth failure returned `duplicate=true`.

| Stage | Result |
|---|---|
| authenticated ingestion | passed: 6 accepted, 1 replay suppressed |
| raw S3 archive | passed: SeaweedFS SDK compatibility confirmed; ingestion archived before broker publish |
| normalization and enrichment | passed for message flow; enriched messages reached detection |
| OpenSearch event index | passed: new documents are written to non-destructive `autosoc-events-v2-*` indices; `file_hashes` is a bounded `flat_object` and is queryable |
| detection | passed: four alerts persisted (`auth_001` through `auth_004`) |
| correlation | passed: four entity/rule-specific incidents, links, ATT&CK mappings and audit records persisted |
| prediction | passed: Markov predictions persisted; duplicate replay created one new durable logical result and the second delivery was suppressed |
| human response approval | not exercised; no destructive response was authorized |
| agent-worker investigation | passed for one lifecycle incident: real Redpanda consumption, persisted evidence retrieval, local Ollama HTTP 200, and durable advisory result |
| frontend rendering of new events | not yet rerun after the OpenSearch repair |

Database integrity checks confirmed no partial incidents after failed correlation transactions; those transactions rolled back before the timestamp and enum repairs. Correlation replay updated existing incidents rather than creating duplicate incident IDs. New prediction writes use a database uniqueness constraint plus a stable SHA-256 input fingerprint; historical rows were retained with unique legacy fingerprints.
