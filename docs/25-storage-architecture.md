# Storage Architecture

The storage architecture dictates specific systems for distinct data characteristics to maintain performance, integrity, and scalability.

## PostgreSQL
- **Responsibility**: Authoritative system of record for all business state.
- **Owned Data**: User mappings, Role references, Data-source configurations, Detection-rule metadata, Alert state, Incident state, Evidence metadata, Approvals, Response actions, Audit logs, Reports, and System configuration.
- **Access Pattern**: Read/Write from FastAPI Control Plane and Background Workers.

## OpenSearch
- **Responsibility**: Fast full-text and aggregational search for high-volume event data.
- **Owned Data**: Normalized security events, Enriched security events, Alert log evidence.
- **Access Pattern**: Write-heavy from Processing Worker; Read-heavy from FastAPI (Analyst search) and Agent Worker (RAG).

## Redis
- **Responsibility**: In-memory ephemeral storage. Never the system of record.
- **Owned Data**: UI caching, API rate-limit state, Temporary workflow states (e.g., LangGraph checkpoints), Distributed locks, Short-lived deduplication windows (e.g., dropping duplicate logs within a 1-second window).
- **Access Pattern**: Extremely high-throughput read/write.

## MinIO
- **Responsibility**: High-capacity object storage (S3-compatible).
- **Owned Data**: Raw-event archives (cold storage), Dataset files for ML, Model artifacts (via MLflow), Generated PDF/CSV report files, Large evidence attachments.
- **Access Pattern**: Write once, read infrequently.

## MLflow (Backed by MinIO and PostgreSQL)
- **Responsibility**: Model registry and tracking.
- **Owned Data**: Experiment parameters, training metrics, model versioning tags.
- **Access Pattern**: Write during training; Read during ML-inference worker startup.

## Vector-Search Capability Decision
- **Decision**: The MVP will utilize **OpenSearch's built-in k-NN vector index** capability.
- **Reasoning**: Log data is already normalized and indexed in OpenSearch. Leveraging its vector capabilities prevents the introduction of an additional database (e.g., Pinecone or pgvector in Postgres), simplifying the local Docker Compose deployment while providing seamless hybrid search capabilities (combining keyword filtering with semantic RAG retrieval).
