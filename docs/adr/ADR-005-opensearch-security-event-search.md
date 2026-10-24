# ADR-005: OpenSearch for Security-Event Search

## Status
Accepted

## Context
AutoSOC must ingest, index, and query millions of security events (Syslog, CloudTrail, NetFlow) rapidly. Analysts and the Agentic AI require fast full-text search and aggregations over structured JSON logs to investigate incidents.

## Decision
We will use OpenSearch as the primary search engine for normalized and enriched security events.

## Alternatives Considered
- **Elasticsearch**: Rejected due to recent licensing changes that complicate use in some environments; OpenSearch provides a fully open-source alternative with compatible APIs.
- **PostgreSQL (JSONB)**: Rejected for full-text log search at scale due to performance limitations and lack of specialized search aggregations compared to Lucene-based engines.
- **Splunk / Commercial SIEMs**: Rejected as this project aims to build an autonomous SOC platform from open-source components.

## Positive Consequences
- Highly scalable full-text search and aggregation capabilities.
- Excellent integration with Python via the `opensearch-py` client.
- Built-in vector search capabilities (k-NN) which can be utilized for RAG workflows.

## Negative Consequences
- High memory and CPU overhead for running OpenSearch locally in Docker Compose.
- Requires careful index management and retention policies to prevent disk exhaustion.

## Security Implications
- Data stored in OpenSearch must be strictly segmented if multi-tenancy is introduced.
- Access to OpenSearch will be brokered through the FastAPI backend to enforce RBAC; direct access by users is prohibited.

## Revisit Conditions
- If resource consumption in the local academic deployment is too high, we may need to tune JVM heaps or limit the retention window drastically.
