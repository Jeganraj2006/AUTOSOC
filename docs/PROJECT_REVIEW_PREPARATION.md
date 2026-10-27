# Project review preparation

## Problem and solution

Security teams need a demonstrable path from heterogeneous telemetry to reviewed response. AutoSOC demonstrates that path locally: authenticated ingestion, durable streaming and storage, deterministic detections/correlation, local advisory AI, human response approval, and auditability. It is not positioned as a replacement for a managed enterprise SIEM/SOAR.

## Review questions and concise answers

1. **What problem does AutoSOC address?** It demonstrates SOC telemetry-to-reviewed-response orchestration.
2. **What enters the system?** Authenticated raw synthetic or supported source telemetry.
3. **How is ingestion authenticated?** Source ID plus a one-time generated API key whose hash is stored.
4. **Where are raw events stored?** SeaweedFS S3-compatible storage.
5. **Why Redpanda?** It decouples ingestion from normalization and downstream workers.
6. **What normalizes events?** The normalization worker and shared event schemas.
7. **Where are normalized events searchable?** OpenSearch.
8. **How are detections made?** Deterministic configured rules plus existing anomaly/ML components.
9. **What is an alert?** A durable detection record with source-event evidence.
10. **What is an incident?** A correlated group of alerts/events with persisted links.
11. **How are ATT&CK mappings handled?** Correlation persists candidate ATT&CK evidence references.
12. **How are predictions handled?** The prediction worker consumes incidents and persists idempotent results.
13. **What uses a real LLM?** The agent worker calls the configured local Ollama model.
14. **Are all graph nodes LLM agents?** No; many nodes are deterministic workflow stages.
15. **How is model output constrained?** The prompt asks for evidence-only advisory analysis and no commands/containment.
16. **Can the model execute an action?** No; response creation/approval/execution occurs through RBAC-protected APIs.
17. **Who can propose responses?** An authorized analyst or administrator role.
18. **Who can approve?** A separate approving role such as administrator.
19. **Can a proposal author approve it?** No.
20. **What was executed in testing?** Only a validated-only dry run.
21. **Was external containment tested?** No, deliberately.
22. **How are duplicate executions avoided?** A unique idempotency key and transaction handling.
23. **How are retries stored?** Redis retry state with bounded exponential backoff and DLQ publication.
24. **What proves an action happened?** PostgreSQL execution/audit records.
25. **How is authentication implemented?** Keycloak OIDC with Auth.js Authorization Code + PKCE.
26. **What JWT checks exist?** Signature, RS256, JWKS, issuer, audience, exp, iat, and sub.
27. **What roles exist?** Administrator, SOC analyst, and read-only viewer (plus compatible audit roles).
28. **How are secrets handled?** Templates contain placeholders; local secrets and credentials remain outside Git.
29. **Are data-source keys recoverable?** No; plaintext is returned once and revocation is one-way.
30. **Can a revoked key ingest?** No; revocation clears its hash and disables the source.
31. **What database is used?** PostgreSQL with additive Alembic migrations.
32. **What is the UI stack?** Next.js, React, TypeScript, and React Query.
33. **What browser widths were checked?** 375, 768, 1280, and 1920 pixels.
34. **What backend test baseline exists?** 19 prior passing tests before Phase 6 additions.
35. **What frontend test baseline exists?** 15 Vitest tests, lint/type/build checks, and authenticated Playwright journeys.
36. **Did an end-to-end browser check ever fail?** Yes, an Ollama timeout; the durable retry later completed and the evidence remains documented.
37. **Why SeaweedFS instead of MinIO?** The previous MinIO image pull was unavailable; SeaweedFS was verified for required S3-compatible local archival behavior.
38. **What makes this non-production-ready?** Dev-mode Keycloak/OpenSearch, no TLS/HA/vault/CI security gate, and incomplete worker telemetry.
39. **What is the key performance limitation?** Local Ollama inference latency is hardware/model-warmth dependent.
40. **What is the next engineering priority?** Consolidate the legacy API graph path, add worker heartbeats/lag metrics, then harden network/TLS/secrets for deployment.
