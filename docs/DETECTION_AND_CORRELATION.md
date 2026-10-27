# Detection and correlation

Normalized events are evaluated by configured deterministic rules. The detection worker persists alerts with idempotency protection and publishes downstream messages. The correlation worker groups related alerts into incidents and persists incident-alert/event evidence links and ATT&CK mappings. The prediction worker consumes incident messages and stores one idempotent logical prediction per input.

The verified local synthetic scenario traversed ingestion, SeaweedFS archival, normalization, detection, alert persistence, correlation, incident/evidence/ATT&CK persistence, prediction, local Ollama investigation, approval, validated-only dry run, and audit logging. It used synthetic addresses and no real containment.
