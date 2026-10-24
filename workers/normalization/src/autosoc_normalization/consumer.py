import json
import logging
import uuid
import asyncio
from datetime import datetime, timezone
from aiokafka import AIOKafkaConsumer
from autosoc_schemas.events import RawSecurityEvent, FailedSecurityEvent
from .config import settings
from .registry import parser_registry
from .enrichment.modules import EnrichmentEngine
from .publisher import EventPublisher
from .storage.opensearch import OpenSearchStorage

logger = logging.getLogger(__name__)

class NormalizationConsumer:
    def __init__(self, publisher: EventPublisher, opensearch: OpenSearchStorage):
        self.publisher = publisher
        self.opensearch = opensearch
        self.enrichment_engine = EnrichmentEngine()
        self.consumer = AIOKafkaConsumer(
            settings.TOPIC_RAW,
            bootstrap_servers=settings.REDPANDA_BROKERS,
            group_id=settings.CONSUMER_GROUP,
            enable_auto_commit=False, # Explicit commit after pipeline success
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
        self.running = False

    async def start(self):
        await self.consumer.start()
        self.running = True
        logger.info(f"Started consuming from {settings.TOPIC_RAW}")
        
        try:
            while self.running:
                msg = await self.consumer.getone()
                await self.process_message(msg)
                await self.consumer.commit()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Consumer loop error: {e}")
        finally:
            await self.consumer.stop()

    async def stop(self):
        self.running = False

    async def process_message(self, msg):
        raw_event = None
        try:
            raw_event = RawSecurityEvent(**msg.value)
        except Exception as e:
            logger.error(f"Failed to deserialize RawSecurityEvent: {e}")
            await self._handle_failure(None, "deserialization", "VALIDATION_ERROR", str(e), msg.value)
            return

        parser = parser_registry.get_parser(raw_event.source_type)
        if not parser:
            logger.warning(f"No parser found for source_type: {raw_event.source_type}")
            await self._handle_failure(raw_event, "normalization", "MISSING_PARSER", "No parser registered")
            return

        try:
            # 1. Normalize
            normalized = parser.parse(raw_event)
            await self.publisher.publish_normalized(normalized)
            
            # 2. Enrich
            enriched = await self.enrichment_engine.enrich_event(normalized)
            await self.publisher.publish_enriched(enriched)
            
            # 3. Index to OpenSearch
            success = await self.opensearch.index_event(enriched)
            if not success:
                logger.error(f"OpenSearch indexing failed for {enriched.event_id}")
                
        except Exception as e:
            logger.error(f"Pipeline error for {raw_event.event_id}: {e}")
            await self._handle_failure(raw_event, "pipeline", "PIPELINE_ERROR", str(e))

    async def _handle_failure(self, raw_event, stage, code, desc, raw_payload=None):
        try:
            failure = FailedSecurityEvent(
                failure_id=uuid.uuid4(),
                ingestion_id=raw_event.ingestion_id if raw_event else None,
                source_id=raw_event.source_id if raw_event else None,
                source_type=raw_event.source_type if raw_event else None,
                received_at=datetime.now(timezone.utc),
                failure_stage=stage,
                failure_reason_code=code,
                failure_description=desc,
                payload_hash=raw_event.payload_hash if raw_event else None,
                trace_id=raw_event.trace_id if raw_event else None,
                retryable=False
            )
            await self.publisher.publish_failure(failure)
        except Exception as e:
            logger.critical(f"Failed to publish failure event! Original error: {desc}. DLQ error: {e}")
