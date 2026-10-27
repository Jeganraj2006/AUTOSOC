# AutoSOC complete project overview

AutoSOC is a local academic SOC demonstration that accepts authenticated telemetry, archives and normalizes it, applies deterministic detections, correlates incidents, persists predictions and local-Ollama investigations, and enforces approval before any response execution. The only execution verified for this release is a validated-only dry run; it never performs containment.

The repository contains a Next.js operations UI, FastAPI read/control API, PostgreSQL, Redis, Redpanda, SeaweedFS, OpenSearch, Keycloak, and six active SOC workers. Twelve Docker services are configured. "Agent" has two meanings: the six-stage LangGraph-style logical workflow is not six containers; the local Ollama inference is performed by the single `agent-worker` container and persisted as an investigation.

Local-development acceptance evidence is in `PHASE5_FINAL_ACCEPTANCE.md`, `PHASE5_BROWSER_E2E_REPORT.md`, and `PHASE5_END_TO_END_VERIFICATION.md`. The first monolithic browser pipeline attempt timed out at Ollama; durable retry later completed the same investigation and browser response verification passed. This is retained as an observed reliability limitation, not erased as a success.
