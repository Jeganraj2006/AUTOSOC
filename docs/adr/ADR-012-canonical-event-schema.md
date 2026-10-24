# ADR-012: OCSF-Inspired Canonical Event Schema

## Status
Accepted

## Context
AutoSOC ingests logs from diverse sources (Syslog, Windows, CloudTrail, NetFlow), each with varying formats and field names (e.g., `src_ip`, `SourceIp`, `ip.src`). Building detection rules and ML models requires a consistent, normalized data format.

## Decision
We will adopt a canonical event schema inspired by the Open Cybersecurity Schema Framework (OCSF) for all normalized events. All incoming raw logs must be mapped to this schema before detection occurs.

## Alternatives Considered
- **Elastic Common Schema (ECS)**: Considered, but OCSF is gaining broader industry adoption as a vendor-agnostic standard.
- **Custom Ad-hoc Schema**: Rejected because it limits interoperability and requires constant refactoring as new data sources are added.

## Positive Consequences
- Detection rules and ML models only need to be written once against the canonical schema.
- Simplifies the Agentic AI's ability to reason about logs.
- Easier to integrate new data sources.

## Negative Consequences
- Writing mapping logic for every new log source is time-consuming.
- Some edge-case data might be lost or stuffed into a generic "unmapped" JSON blob if it doesn't fit the schema.

## Security Implications
- Normalization ensures that critical fields (like timestamps and IPs) are strictly typed, preventing injection attacks disguised as malformed logs.

## Revisit Conditions
- If OCSF proves too complex or verbose for our specific use cases, we will simplify it while retaining the core concept of a canonical schema.
