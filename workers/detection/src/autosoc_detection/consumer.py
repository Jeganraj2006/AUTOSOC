import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
from autosoc_schemas.events.normalized import EnrichedSecurityEvent
from autosoc_detection.engine.core import DetectionEngine
from autosoc_detection.alerts.publisher import AlertPublisher
from autosoc_detection.alerts.persistence import AlertPersistence
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class DetectionConsumer:
    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topic: str,
        engine: DetectionEngine,
        publisher: AlertPublisher,
        persistence: AlertPersistence
    ):
        self.topic = topic
        self.engine = engine
        self.publisher = publisher
        self.persistence = persistence
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="latest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8"))
        )

    async def start(self):
        await self.consumer.start()
        logger.info(f"Started detection consumer on topic {self.topic}")
        try:
            async for msg in self.consumer:
                await self.process_message(msg.value)
        finally:
            await self.consumer.stop()

    async def process_message(self, data: dict):
        try:
            event = EnrichedSecurityEvent(**data)
            alerts = await self.engine.evaluate_event(event)
            
            for alert in alerts:
                logger.warning(f"ALERT GENERATED: {alert.title} (Rule: {alert.rule_id})")
                try:
                    await self.persistence.persist_alert(alert)
                    await self.publisher.publish(alert)
                except Exception as e:
                    logger.error(f"Failed to persist/publish alert {alert.detection_id}: {str(e)}")
                    
        except ValidationError as e:
            # If the event doesn't match EnrichedSecurityEvent, we log and skip
            logger.debug(f"Skipping malformed event: {str(e)[:100]}")
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}")
