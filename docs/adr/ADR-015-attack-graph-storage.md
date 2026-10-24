# ADR-015: Initial Graph Storage Strategy

## Status
Accepted

## Context
AutoSOC must generate attack graphs mapping alerts to MITRE ATT&CK tactics and techniques. 

## Decision
We will prefer storing graph relationships (nodes and edges) natively in PostgreSQL using relational tables (e.g., `incident_nodes`, `incident_edges`) rather than introducing a dedicated graph database (like Neo4j) for the MVP.

## Alternatives Considered
- **Neo4j**: Rejected due to the operational overhead of adding another database technology for a feature that initially only requires shallow traversals.

## Positive Consequences
- Keeps the infrastructure footprint small.
- Leverages existing SQLAlchemy models and Alembic migrations.

## Negative Consequences
- Deep recursive queries (finding complex paths longer than 3-4 hops) are inefficient in SQL compared to a native graph database (Cypher).

## Security Implications
- Relational integrity ensures that edges cannot exist without valid nodes, preventing graph corruption.

## Revisit Conditions
- If the complexity of the Attack-Progression Prediction requires deep graph traversals that perform poorly in PostgreSQL, we will evaluate introducing a dedicated graph database or extracting the graph entirely in-memory using NetworkX in Python.
