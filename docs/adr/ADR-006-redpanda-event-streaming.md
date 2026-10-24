# ADR-006: Redpanda for Event Streaming

## Status
Accepted

## Context
AutoSOC must process high volumes of security events. Ingestion, normalization, ML inference, and alert generation must be decoupled to prevent bottlenecks and ensure resilience against downstream failures.

## Decision
We will use Redpanda as the event streaming platform, utilizing Kafka-compatible clients in Python (e.g., `confluent-kafka` or `aiokafka`).

## Alternatives Considered
- **Apache Kafka**: Rejected because it requires ZooKeeper (or Kraft) and is significantly heavier to run in a local Docker Compose environment. Redpanda provides a single-binary, Kafka-compatible alternative.
- **RabbitMQ**: Rejected because it is primarily a message queue, lacking the robust log-retention and replay capabilities inherent to Kafka-like append-only logs, which are crucial for security event streaming and ML reprocessing.
- **Redis Pub/Sub**: Rejected because it lacks persistence and guaranteed delivery semantics required for audit and security events.

## Positive Consequences
- High throughput and low latency.
- Decouples ingestion from processing, allowing workers to scale independently.
- Kafka API compatibility allows the use of standard, well-tested Python libraries.
- Easy local deployment via a single Docker container.

## Negative Consequences
- Introduces distributed system complexity (e.g., dealing with consumer groups, partition rebalancing, and exactly-once processing semantics).

## Security Implications
- Redpanda topics containing raw or parsed security logs may contain sensitive data; access to the broker must be restricted.

## Revisit Conditions
- If the Kafka API compatibility layer in Redpanda introduces unforeseen bugs with our chosen Python clients, we may switch to Apache Kafka in Kraft mode.
