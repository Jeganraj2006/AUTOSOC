import logging
from opensearchpy import AsyncOpenSearch
from autosoc_schemas.events import NormalizedSecurityEvent, EnrichedSecurityEvent

logger = logging.getLogger(__name__)

class OpenSearchStorage:
    def __init__(self, hosts: str):
        self.client = AsyncOpenSearch(
            hosts=[hosts],
            use_ssl=False,
            verify_certs=False,
        )
        self.index_name_prefix = "autosoc-events-v1"

    async def initialize_templates(self):
        """
        Creates the index template to prevent mapping explosion.
        """
        template = {
            "index_patterns": [f"{self.index_name_prefix}-*"],
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "dynamic": "strict", # Explicit mappings only
                "properties": {
                    "event_id": {"type": "keyword"},
                    "normalized_event_id": {"type": "keyword"},
                    "ingestion_id": {"type": "keyword"},
                    "source_id": {"type": "keyword"},
                    "source_type": {"type": "keyword"},
                    "schema_version": {"type": "integer"},
                    "event_time": {"type": "date"},
                    "received_at": {"type": "date"},
                    "normalized_at": {"type": "date"},
                    "timestamp_quality": {"type": "keyword"},
                    "event_category": {"type": "keyword"},
                    "event_type": {"type": "keyword"},
                    "event_action": {"type": "keyword"},
                    "event_outcome": {"type": "keyword"},
                    "severity_source": {"type": "keyword"},
                    "message": {"type": "text"},
                    "source_ip": {"type": "ip"},
                    "destination_ip": {"type": "ip"},
                    "source_port": {"type": "integer"},
                    "destination_port": {"type": "integer"},
                    "protocol": {"type": "keyword"},
                    "username": {"type": "keyword"},
                    "hostname": {"type": "keyword"},
                    "process_name": {"type": "keyword"},
                    "command_line": {"type": "text"},
                    "raw_event_reference": {"type": "keyword"},
                    "normalization_confidence": {"type": "keyword"},
                    "normalization_warnings": {"type": "keyword"},
                    
                    # Enriched Fields
                    "asset_environment": {"type": "keyword"},
                    "asset_criticality": {"type": "keyword"},
                    "geo_country": {"type": "keyword"},
                    "ip_reputation_status": {"type": "keyword"},
                    "candidate_mitre_techniques": {"type": "keyword"}
                }
            }
        }
        try:
            await self.client.indices.put_template(
                name="autosoc_events_template",
                body=template
            )
            logger.info("OpenSearch template initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize OpenSearch template: {e}")

    async def index_event(self, event: EnrichedSecurityEvent) -> bool:
        """
        Indexes an enriched event into the rolling index.
        """
        try:
            index_name = f"{self.index_name_prefix}-{event.normalized_at.strftime('%Y.%m.%d')}"
            
            doc = event.model_dump(exclude_none=True)
            # Serialize datetimes to ISO
            for k, v in doc.items():
                if hasattr(v, "isoformat"):
                    doc[k] = v.isoformat()
                    
            # Use normalized_event_id as document ID to ensure idempotency
            await self.client.index(
                index=index_name,
                id=str(event.normalized_event_id),
                body=doc
            )
            return True
        except Exception as e:
            logger.error(f"Failed to index event {event.event_id}: {e}")
            return False

    async def close(self):
        await self.client.close()
