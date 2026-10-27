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
        # Mapping changes are introduced through a new index generation.  Existing
        # v1 indices remain read-only and searchable; new pipeline documents use v2.
        self.index_name_prefix = "autosoc-events-v2"

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
                    "timezone_original": {"type": "keyword"},
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
                    "transport": {"type": "keyword"},
                    "direction": {"type": "keyword"},
                    "bytes_in": {"type": "long"},
                    "bytes_out": {"type": "long"},
                    "packets_in": {"type": "long"},
                    "packets_out": {"type": "long"},
                    "session_duration": {"type": "long"},
                    "username": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "user_domain": {"type": "keyword"},
                    "user_type": {"type": "keyword"},
                    "privilege_level": {"type": "keyword"},
                    "hostname": {"type": "keyword"},
                    "host_id": {"type": "keyword"},
                    "host_ip": {"type": "ip"},
                    "operating_system": {"type": "keyword"},
                    "process_name": {"type": "keyword"},
                    "process_id": {"type": "integer"},
                    "process_path": {"type": "keyword"},
                    "command_line": {"type": "text"},
                    "parent_process_name": {"type": "keyword"},
                    "parent_process_id": {"type": "integer"},
                    "file_name": {"type": "keyword"},
                    "file_path": {"type": "keyword"},
                    # Hash algorithm names are data, not mappings. flat_object
                    # retains key/value search without unbounded field creation.
                    "file_hashes": {"type": "flat_object"},
                    "authentication_method": {"type": "keyword"},
                    "authentication_result": {"type": "keyword"},
                    "failure_reason": {"type": "keyword"},
                    "cloud_provider": {"type": "keyword"},
                    "cloud_account_id": {"type": "keyword"},
                    "cloud_region": {"type": "keyword"},
                    "resource_type": {"type": "keyword"},
                    "resource_id": {"type": "keyword"},
                    "api_operation": {"type": "keyword"},
                    "cluster_name": {"type": "keyword"},
                    "namespace": {"type": "keyword"},
                    "pod_name": {"type": "keyword"},
                    "container_name": {"type": "keyword"},
                    "service_account": {"type": "keyword"},
                    "raw_event_reference": {"type": "keyword"},
                    "raw_payload_hash": {"type": "keyword"},
                    "parser_name": {"type": "keyword"},
                    "parser_version": {"type": "keyword"},
                    "normalization_confidence": {"type": "keyword"},
                    "normalization_warnings": {"type": "keyword"},
                    "trace_id": {"type": "keyword"},
                    "request_id": {"type": "keyword"},
                    
                    # Enriched Fields
                    "asset_environment": {"type": "keyword"},
                    "asset_criticality": {"type": "keyword"},
                    "asset_category": {"type": "keyword"},
                    "asset_business_role": {"type": "keyword"},
                    "asset_owner_reference": {"type": "keyword"},
                    "user_privilege_category": {"type": "keyword"},
                    "user_department": {"type": "keyword"},
                    "is_service_account": {"type": "boolean"},
                    "geo_country": {"type": "keyword"},
                    "geo_region": {"type": "keyword"},
                    "geo_city": {"type": "keyword"},
                    "asn": {"type": "keyword"},
                    "ip_classification": {"type": "keyword"},
                    "ip_reputation_status": {"type": "keyword"},
                    "vuln_count": {"type": "integer"},
                    "vuln_highest_severity": {"type": "keyword"},
                    "vuln_cve_references": {"type": "keyword"},
                    "entity_first_seen": {"type": "date"},
                    "entity_last_seen": {"type": "date"},
                    "event_frequency": {"type": "keyword"},
                    "is_rare_entity": {"type": "boolean"},
                    "ti_indicator_match_refs": {"type": "keyword"},
                    "ti_source_refs": {"type": "keyword"},
                    "ti_confidence": {"type": "keyword"},
                    "ti_expiration": {"type": "date"},
                    "candidate_mitre_techniques": {"type": "keyword"},
                    "candidate_mitre_confidence": {"type": "keyword"},
                    "candidate_mitre_source": {"type": "keyword"}
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
