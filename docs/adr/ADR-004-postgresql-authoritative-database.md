# ADR-004: PostgreSQL as Authoritative Database

## Status
Accepted

## Context
AutoSOC requires a robust, ACID-compliant data store for critical business state, including user references, RBAC mappings, detection rules, alert states, incident metadata, and audit logs. Data integrity and immutability for audit records are paramount.

## Decision
We will use PostgreSQL as the primary authoritative relational database, managed via SQLAlchemy and Alembic.

## Alternatives Considered
- **MySQL / MariaDB**: PostgreSQL offers superior support for complex JSONB queries and advanced extensions (like pgvector for potential future RAG use).
- **MongoDB**: Rejected because strict schema enforcement, complex relational queries (e.g., correlating alerts to incidents to responses), and ACID transactions are better handled by a relational database.

## Positive Consequences
- High data integrity and reliable transactions.
- Strong ecosystem support in Python (SQLAlchemy).
- JSONB support allows for flexible storage of unstructured metadata alongside structured relational data.

## Negative Consequences
- Scaling PostgreSQL horizontally is complex compared to NoSQL databases.

## Security Implications
- PostgreSQL supports row-level security and fine-grained access control, though we will primarily enforce authorization at the application layer (FastAPI).

## Revisit Conditions
- If the volume of alert metadata exceeds PostgreSQL's single-node write capacity, we will evaluate sharding or moving high-volume transient data to a time-series or NoSQL database.
