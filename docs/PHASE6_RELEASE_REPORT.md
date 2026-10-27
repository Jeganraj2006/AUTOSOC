# Phase 6 release report — local development

## Release posture

AutoSOC is prepared as a reproducible **local-development and academic demonstration** release. Production readiness is explicitly not claimed.

## Working-tree protection

Before Phase 6 changes, a source-only recovery archive was verified at `E:\AUTOSOC\checkpoints\autosoc-phase6-source-only-20261027-070852.zip` (633 files; SHA-256 `1AF4E440A7923050E71A90ABDE6F9A95266954A28492945E0216C20511171F36`). It contains tracked and untracked source, migrations, tests, Compose configuration, and documentation while excluding Git metadata, env files, secrets, generated artifacts, models, databases, caches, and runtime data. Restore by extracting into a clean directory, copying a newly generated `.env`, and running the deployment guide. The existing Phase 4 checkpoint was left untouched.

## Phase 6 audited and corrected items

| Finding | Result |
| --- | --- |
| Repeat setup reset Keycloak passwords | Fixed: normal reconciliation preserves existing passwords; rotation is explicit. |
| Development viewer realm role | Fixed bootstrap now assigns `viewer`; existing `auditor` role remains compatible/read-only. |
| Ingestion-key revocation | Fixed: privileged `POST /data-sources/{id}/revoke` clears the hash and disables the source with an audit entry. |
| Token failure logging | Fixed: logs only exception type, not token-derived detail. |
| Key-generation/read exposure | Verified: `secrets.token_urlsafe(32)`, SHA-256 storage, one-time create response, list/detail schemas omit hash/key. |
| SeaweedFS | Compose pins `chrislusf/seaweedfs:4.50` to `sha256:c265...64860`; prior Phase 5 evidence verified authenticated S3 upload/download/persistence. |
| Docker services | 12 containers observed up; five expose Docker health checks. Worker functional status must be supported by message/persistence evidence, not container state. |
| Frontend dependency audit | Fixed: upgraded Next.js/ESLint config to 16.4.1 and Zod to the resolved 4.6.7 lockfile version; post-update `pnpm audit --prod` reported 0 critical, 0 high, 0 moderate, 0 low. |

The new data-source security browser/API regression passed against the current-source verification API: administrator creation returned a one-time `asoc_` key, list output contained neither plaintext key nor hash, revocation disabled the source, and the ingestion service returned HTTP 403 when that revoked source/key was used.

## Fresh Phase 6 browser evidence

The patched Next.js 16.4.1 server served `/login` successfully. Playwright ran 7 authenticated administrator/analyst/viewer/responsive/logout checks successfully and one analyst-proposal → administrator-approval → `validated_only` dry-run test successfully. The full fresh browser pipeline then failed at a generic durable-result waiter. Direct follow-up evidence for that same new synthetic source showed six indexed normalized events, a correlated brute-force incident with rule `corr_001_bruteforce_success`, an idempotent prediction, and a completed local-Ollama agent execution. The full test was not relabelled as passed. Its waiter now reports the missing stage explicitly on future runs.

## Deliberately retained limitations

The Phase 5.5 accepted baseline's monolithic Playwright pipeline timeout is retained in the evidence. The fresh Phase 6 full-browser waiter failure is retained too. OpenSearch/Compose security and worker-health limitations are listed in `KNOWN_LIMITATIONS.md`. SBOM tooling was not installed locally; release documentation records this as a gap rather than inventing a scan result.

## Archive status

Created and integrity-tested: `E:\AUTOSOC\releases\AutoSOC-Final-Local-Development-Release-20261027.zip` (653 source files). It includes the safe API and Docker `.env.example` templates and excludes env files, credential handoffs, databases, runtime logs, model downloads, caches, `.git`, and existing checkpoint archives. `7z t` passed and forbidden-entry enumeration returned zero. Compute a current SHA-256 with `Get-FileHash -Algorithm SHA256` after copying the archive.

The final post-verification archive supersedes that earlier archive: `E:\AUTOSOC\releases\AutoSOC-Final-Local-Development-Release-20261027-final.zip`. Its final hash is computed only after its sources are frozen; its `7z t` test, forbidden-entry enumeration, and common cloud-key/private-key scan passed.

## Final verification update

The previously generic pipeline waiter exposed three real defects, all repaired and regression-tested: (1) global suppression of stateless detections hid alerts from later independent sources, (2) the events endpoint used incompatible field sorts across retained v1 and v2 OpenSearch indices, and (3) the incident-alert read used a lossy legacy foreign key instead of durable evidence links. The waiter is now stage-labelled and fails immediately for a non-successful events API response.

A new complete browser run passed in 1.2 minutes. It created a new synthetic source and six events, verified four durable alert links, a correlated incident, one prediction, one completed local-Ollama investigation, an analyst proposal, administrator approval, validated-only dry-run execution, audit records, and the filtered Response Management UI. The full final Playwright suite then passed 9 tests with 1 intentional, data-dependent skip (the separate response test requires a caller-supplied fresh incident ID; the full pipeline covers that lifecycle itself). See `FINAL_RELEASE_VERIFICATION.md` for the final archive checksum and commit-readiness assessment.
