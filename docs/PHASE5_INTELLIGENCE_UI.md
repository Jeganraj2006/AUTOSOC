# Phase 5.3 intelligence UI

## Scope completed

| Workspace | Source of truth | Implemented behavior |
| --- | --- | --- |
| Detection intelligence | `GET /rules`, existing `POST /events/detect` | Rule metadata inventory, local filtering of the returned window, inline rule detail, ATT&CK references where returned, and a clearly separate anomaly-evaluation result view. |
| Attack predictions | `GET /incidents/{id}/predictions/latest`, `GET /incidents/{id}/predictions`, `POST /incidents/{id}/predictions/recompute` | Incident selector, persisted prediction metadata, observed/predicted technique separation, API-provided numeric estimates only, model/version display, limitations, history, and incident navigation. |
| AI Investigation Center | `GET /incidents`, `GET /{id}/agents`, `POST /{id}/agents/investigate` | Incident-scoped execution history, RBAC-gated start action, persisted graph telemetry, model metadata, retry counts, evidence citations, safe failure messaging, and stored result sections. |

## Architecture representation

AutoSOC has graph-processing stages and an Ollama-backed risk-assessment step. The UI deliberately presents a single investigation workflow with persisted stages; it does not claim that each graph node is an independently operating AI agent. Model output and deterministic execution telemetry are presented in separate areas.

## Incident integration

- The incident detail prediction panel now uses the authenticated TanStack Query prediction hooks.
- Recompute controls are role-aware in the interface and remain enforced by the backend permission endpoint.
- The incident investigation panel now recognizes the lowercase persisted execution statuses and links users to the AI Investigation Center for persisted findings and evidence.
- Response approval and validated-only dry-run controls were preserved; no containment action was introduced.

## Deliberate omissions

- Rule execution counts, matching events, generated alerts, and related incidents are not returned by the rule metadata API.
- There is no global prediction or investigation collection API, so dashboard-style global totals are not displayed.
- The API does not expose a reliable prediction confidence field. The UI displays probability or score only when a technique record actually provides it.
- Unstructured internal diagnostic payloads are not rendered to operators. A persisted failure reason is shown when available.

## Regression coverage

The intelligence helper tests cover returned-rule filtering including empty results, ATT&CK reference parsing, model metadata presence, actual numeric prediction estimates, investigation-state labeling, and evidence-citation de-duplication. Existing tests retain coverage for event query filters, alert posture, viewer-safe triage visibility, response dry-run eligibility, and incident routing.
