# Phase 5.5 end-to-end verification

Date: 2026-10-26. Results below distinguish executed checks from blocked checks.

## Final browser and fresh pipeline acceptance update

An isolated source authenticated to the real ingestion worker and produced six raw SeaweedFS objects. The pipeline created correlated incidents, durable alerts/evidence/ATT&CK mappings, predictions, and a local-Ollama investigation. The response portion used the same fresh correlated incident `33690706-9e11-42f7-8ce3-4e13c689d10a`: analyst proposal, administrator approval, and validated-only dry run all persisted.

| Stage | Result |
| --- | --- |
| Raw authenticated ingestion and duplicate suppression | Passed — six accepted, repeat payload returned duplicate. |
| SeaweedFS raw archival | Passed — six objects under the isolated source prefix. |
| Normalization/OpenSearch/detection/correlation | Passed — worker logs and incident/alert relationships persisted. |
| Evidence/ATT&CK/prediction | Passed — 6 alert links, 4 event links, 4 ATT&CK mappings, prediction persisted. |
| Local Ollama investigation | Passed after one recoverable timeout/retry — completed using `llama3.2:3b`, retry count 1. |
| Approval/execution/audit | Passed — execution `succeeded`, `verified`, `validated_only`; `response.execution_requested` audit persisted. |
| Browser OIDC and responsive checks | Passed — 7 role/viewport checks plus the approved-response browser flow. |

## Final authorized API verification update

A temporary public Keycloak client, `autosoc-phase55-verify`, was created with direct access grants solely for this local verification. It obtained normal signed tokens for the real administrator, analyst, and viewer identities and was removed after both verification passes. The established frontend client and JWT validation were not changed.

| Contract / case | Result |
| --- | --- |
| Administrator token and `/auth/me` | Passed — `200`. |
| Event category/source/source-IP/destination-IP/text/paging | Passed — combined `powershell` query returned `200`, total `10`, returned `2`, stable page limit `2`. |
| Event file-hash path | Passed — a controlled authenticated CSV upload returned `200`; combined SHA-256 filter returned exactly one event. |
| Event invalid page size | Passed — authenticated `limit=251` returned `422`. |
| Alert paged list and severity/status/incident filters | Passed — list `200`, total `36`; sampled filters returned `200`. No current alert has `rule_id`, so no rule-filter fixture exists. |
| Global responses | Passed — Admin, Analyst, Viewer each received `200`; proposal detail returned persisted approval/execution history. An Analyst filtering another creator received `403`. |
| Audit history | Passed — Admin/Viewer `200`, Analyst `403`; action/time/page filtering succeeded and sampled nested metadata had no unredacted sensitive value. |
| Dashboard aggregate comparison | Passed — API `36|7|1|12|0|0` exactly matched direct read-only PostgreSQL counts. |
| Operational health | Passed — six direct dependencies are healthy; all workers are correctly `unknown` without heartbeats. |
| Anonymous and Viewer denial | Passed — anonymous response read `401`; Viewer propose and execute attempts each `403`. |

| Check | Status | Current evidence |
| --- | --- | --- |
| Docker infrastructure | Passed | `docker compose ps` showed all 12 configured services up; PostgreSQL, Redpanda, Redis, OpenSearch, and SeaweedFS reported their configured health states. |
| API restart | Passed | Existing port-8000 Uvicorn process restarted safely and reported startup completion. |
| Database migration | Passed | `alembic upgrade head` advanced from `g46f7b8c9d0e` to `h57g8c9d0e1f`. |
| New-route unauthenticated protection | Passed | `/events`, `/alerts/search`, `/responses`, `/audit/`, and `/health/operations` each returned `401` without a bearer token. |
| Backend regression | Passed | `uv run --group dev pytest -q`: 19 passed. |
| Frontend lint | Passed | `pnpm lint`: 0 errors, 0 warnings. |
| Frontend strict TypeScript | Passed | `pnpm exec tsc --noEmit`. |
| Frontend unit tests | Passed | `pnpm exec vitest run`: 4 files, 15 tests passed. |
| Frontend production build | Passed | `pnpm build` compiled successfully and produced `.next/BUILD_ID`. Non-failing Next workspace-root and middleware-convention warnings remain. |
| Authenticated new API contracts | Passed | Temporary least-privileged verification client used normal signed Keycloak tokens and was removed afterward. |
| Browser journeys / responsive viewports | Blocked | Browser bridge exposes no controllable local tab. No unsupported browser-security workaround was used. |
| Fresh full synthetic pipeline | Partial | Authenticated synthetic event upload/search and persisted response/audit reads were verified; a fresh complete ingestion-to-investigation-to-response pipeline was not run in this pass. |

## Manual OIDC verification plan

1. Sign in through the running AutoSOC login page using the existing Keycloak flow.
2. In Events, exercise text, IP, source, severity, time, sort, and page filters; confirm totals change on the server.
3. In Alerts, search by an existing identifier/title and page through results.
4. In Response Management, confirm proposal review/execution records match incident detail. Execute only an approved dry run and confirm the explicit validated-only result.
5. In Audit Activity, confirm proposal, approval/rejection, and dry-run records appear without sensitive metadata.
6. In System Health, confirm unavailable/unknown states are distinguishable from healthy.
7. Repeat read-only navigation as Viewer and mutation/approval steps as Analyst/Administrator to confirm RBAC.

No real containment or external response action was executed.
