# ADR 032: Redpanda Python Client

## Status
Accepted

## Context
Phase 6 requires a stable, high-performance Kafka-compatible client to publish raw security events to Redpanda. The ingestion API is built on FastAPI, which is inherently asynchronous. We must choose between `confluent-kafka` (which relies on `librdkafka` and thread-pools) and `aiokafka` (which is native `asyncio`). 

## Decision
We will use **`aiokafka`**.

## Alternatives
- **`confluent-kafka`**: Highly mature, C-extension based. However, integrating it safely into an `asyncio` event loop requires running the producer in a thread pool executor to avoid blocking the API worker threads during timeouts.
- **`kafka-python`**: Deprecated, lacks active Python 3.12+ support without community forks.

## Positive Consequences
- Native `asyncio` integration, ensuring zero event-loop blocking during network stalls.
- Seamless compatibility with FastAPI and `asynccontextmanager`.
- Lower thread context-switching overhead for high-concurrency ingestion.

## Negative Consequences
- `aiokafka` is slightly less performant in raw throughput compared to C-based `librdkafka` for extremely massive batches, but for our bounded payload limits, the overhead is negligible.
- Might lag slightly behind `librdkafka` in supporting the newest Kafka protocol features.

## Security Implications
No direct security implications, as TLS and SASL (if configured) are supported by `aiokafka`.

## Revisit Conditions
If ingestion throughput exceeds `aiokafka`'s capabilities (e.g. > 50,000 EPS per worker), we will evaluate switching to `confluent-kafka` with robust background thread pools.
