# AI agent verification

## Verified path

The `agent-worker` now consumes `security.incidents` with manual Kafka commits. For a retained lifecycle incident it retrieved persisted alert evidence from PostgreSQL, sent a bounded evidence-only prompt to `http://host.docker.internal:11434/api/generate`, received HTTP 200 from the local `llama3.2:3b` model, and persisted `agent_executions.result_data`.

The stored result deliberately separates `observed_evidence`, raw `model_analysis`, and the notice that analyst approval is required. It creates no automatic containment action and has no destructive tools.

## Counts

- Logical graph nodes identified: 11.
- Independent AI agents verified: 1 (the evidence-grounded local-Ollama investigation path).
- Deterministic worker-graph stages verified: 7 (one complete linear graph path).
- Independently tested local-model investigation paths: 1.
- End-to-end persisted AI investigations: 1.
- Unverified independent logical nodes: 10.

## Limitations

The eleven entries are graph nodes, not eleven independent AI agents. The legacy API graph still includes procedural/static nodes and remains unverified. The worker now persists a running state before inference and a failed state after inference errors, but bounded retries, dead-letter routing, and per-node persistent status records remain future work.
