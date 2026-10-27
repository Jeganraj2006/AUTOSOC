# Phase 3/4 security review

- SeaweedFS credentials were verified by authenticated SDK operations; no credential values are documented here.
- The OpenSearch repair preserves strict top-level mappings and uses `flat_object` for untrusted hash-algorithm keys, preventing telemetry-controlled field explosion. Existing v1 indices were not deleted.
- Prediction idempotency is enforced in PostgreSQL through `uq_predictions_logical_input`; Kafka offsets are committed only after durable processing.
- Agent-worker prompts contain only retrieved incident/alert evidence. Its local-model output is advisory, persisted for review, and cannot execute response actions.
- Response recommendation, approval, execution, and audit endpoints retain separate permissions. Their complete browser/API lifecycle is still pending verification.
- Development OpenSearch security-plugin/TLS settings remain pre-existing development-only configuration and are not production suitable.
