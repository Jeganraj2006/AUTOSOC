import json
import logging
from aiokafka import AIOKafkaProducer
from autosoc_schemas.events import NormalizedSecurityEvent, EnrichedSecurityEvent, FailedSecurityEvent
from .config import settings

logger = logging.getLogger(__name__)

class EventPublisher:
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.REDPANDA_BROKERS,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
        )
        
    async def start(self):
        await self.producer.start()
        
    async def stop(self):
        await self.producer.stop()
        
    async def publish_normalized(self, event: NormalizedSecurityEvent):
        try:
            await self.producer.send_and_wait(
                settings.TOPIC_NORMALIZED,
                event.model_dump(exclude_none=True),
                key=str(event.source_id).encode()
            )
        except Exception as e:
            logger.error(f"Failed to publish normalized event: {e}")
            raise
            
    async def publish_enriched(self, event: EnrichedSecurityEvent):
        try:
            await self.producer.send_and_wait(
                settings.TOPIC_ENRICHED,
                event.model_dump(exclude_none=True),
                key=str(event.source_id).encode()
            )
        except Exception as e:
            logger.error(f"Failed to publish enriched event: {e}")
            raise

    async def publish_failure(self, event: FailedSecurityEvent):
        try:
            await self.producer.send_and_wait(
                settings.TOPIC_FAILED,
                event.model_dump(exclude_none=True),
                key=str(event.failure_id).encode()
            )
        except Exception as e:
            logger.error(f"Failed to publish failure event: {e}")
            raise
