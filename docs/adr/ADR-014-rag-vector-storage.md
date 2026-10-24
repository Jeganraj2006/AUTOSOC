# ADR-014: Vector Storage Approach for RAG

## Status
Accepted

## Context
The Agentic AI requires a Retrieval-Augmented Generation (RAG) system to query historical logs, threat intelligence, and playbooks based on semantic similarity.

## Decision
We will use OpenSearch's built-in k-NN vector search capabilities for RAG storage rather than introducing a dedicated vector database (like Milvus, Qdrant, or Pinecone) or using PostgreSQL's `pgvector`.

## Alternatives Considered
- **Dedicated Vector DB (Pinecone/Milvus)**: Rejected to minimize the number of infrastructure components required for the local MVP.
- **PostgreSQL (pgvector)**: Considered, but OpenSearch is already handling our massive log ingestion and full-text search. Keeping logs and their vector embeddings in the same system simplifies the architecture.

## Positive Consequences
- Reduces infrastructure complexity (reusing OpenSearch).
- Allows hybrid search (combining keyword search with vector similarity) natively within OpenSearch.

## Negative Consequences
- OpenSearch k-NN requires significant memory for HNSW graphs.

## Security Implications
- Vector representations of sensitive data are subject to the same access controls as the raw data in OpenSearch.

## Revisit Conditions
- If OpenSearch memory usage becomes prohibitive, we will evaluate moving vector storage to PostgreSQL with `pgvector` or delaying RAG implementation until Phase 15.
