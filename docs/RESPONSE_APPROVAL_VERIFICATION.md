# Response approval verification

## Verified result

The full approval lifecycle is verified with real Keycloak-authenticated API requests and isolated synthetic records. All executions used `dry_run`; the returned result explicitly states `validated_only`, and no external containment action was attempted.

| Control | Status | Evidence |
| --- | --- | --- |
| Analyst creates recommendation | Passed | Proposal and audit records persisted. |
| Analyst requests review | Passed | Pending approval and audit records persisted. |
| Administrator approves | Passed | Approved recommendation can execute a dry run. |
| Administrator rejects | Passed | Rejected proposal status and audit persisted. |
| Rejected execution prevention | Passed | HTTP `400`, no execution row. |
| Pending execution prevention | Passed | HTTP `400`, no execution row. |
| Viewer read-only enforcement | Passed | Viewer proposal, approval, and execute attempts all returned `403`. |
| Unauthenticated enforcement | Passed | Execute attempt returned `401`. |
| Sequential idempotency | Passed | Two `200` responses map to one execution record. |
| Concurrent idempotency | Passed | Two concurrent `200` responses map to one execution record. |
| Stale queued dry-run recovery | Passed | The existing row is completed rather than duplicated. |
| Audit attribution | Passed | Execution-request audit is attributed to `autosoc_admin`. |

The final concurrent proof used proposal `c815b2ab-c910-43af-828b-e01645fe8f04` and execution `f3f6e227-7494-4192-8b92-d3e46d7f7e93`; PostgreSQL records one completed row, not one per request.

## Safety boundary

The implementation never auto-runs non-dry-run or external containment actions on a retry. A non-terminal non-dry-run request remains queued for an explicit executor and human-approved workflow.
