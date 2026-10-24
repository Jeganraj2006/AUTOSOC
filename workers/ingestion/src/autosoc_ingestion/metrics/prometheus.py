from prometheus_client import Counter, Histogram

# Low-cardinality labels: source_type, status
INGESTION_EVENTS_TOTAL = Counter(
    'autosoc_ingestion_events_total',
    'Total number of events processed by ingestion',
    ['source_type', 'status'] # status: accepted, rejected, duplicate, failed
)

INGESTION_PAYLOAD_BYTES = Histogram(
    'autosoc_ingestion_payload_bytes',
    'Size of ingested raw event payloads',
    ['source_type']
)

REDPANDA_PUBLISH_LATENCY = Histogram(
    'autosoc_ingestion_redpanda_publish_seconds',
    'Latency to publish raw events to Redpanda',
    ['topic']
)

MINIO_ARCHIVE_LATENCY = Histogram(
    'autosoc_ingestion_minio_archive_seconds',
    'Latency to archive raw events to MinIO',
    ['bucket']
)
