import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from aiokafka import AIOKafkaConsumer
from autosoc_schemas.events.normalized import EnrichedSecurityEvent
from autosoc_schemas.events.raw import FailedSecurityEvent
from autosoc_api.services.worker_reliability import RedisRetryState
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
        persistence: AlertPersistence,
        retry_state: RedisRetryState,
    ):
        self.topic = topic
        self.engine = engine
        self.publisher = publisher
        self.persistence = persistence
        self.retry_state = retry_state
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="latest",
            enable_auto_commit=False,
            value_deserializer=lambda m: json.loads(m.decode("utf-8"))
        )

    async def start(self):
        await self.consumer.start()
        logger.info(f"Started detection consumer on topic {self.topic}")
        try:
            async for msg in self.consumer:
                message_key = self.retry_state.message_key(msg.topic, msg.partition, msg.offset)
                while True:
                    processed = await self.process_message(msg.value)
                    if processed:
                        await self.retry_state.acknowledge(message_key)
                        await self.consumer.commit()
                        break

                    decision = await self.retry_state.record_failure(
                        message_key,
                        RuntimeError("detection processing was not durable"),
                    )
                    if decision.exhausted:
                        try:
                            await self._publish_retry_exhausted(msg.value, msg, decision.attempt)
                        except Exception:
                            logger.exception("Detection DLQ publish failed; retaining Kafka offset")
                            await asyncio.sleep(decision.delay_seconds)
                            continue
                        logger.error("Retry exhausted for detection message %s", message_key)
                        await self.retry_state.acknowledge(message_key)
                        await self.consumer.commit()
                        break
                    await asyncio.sleep(decision.delay_seconds)
        finally:
            await self.consumer.stop()

    async def _publish_retry_exhausted(self, data: dict, msg, retry_count: int) -> None:
        await self.publisher.publish_failure(
            FailedSecurityEvent(
                failure_id=uuid.uuid4(),
                source_id=data.get("source_id"),
                source_type="normalized_event",
                received_at=datetime.now(timezone.utc),
                failure_stage="detection",
                failure_reason_code="RETRY_EXHAUSTED",
                failure_description="Detection failed after bounded retries",
                trace_id=data.get("trace_id"),
                retryable=False,
                retry_count=retry_count,
                safe_metadata={
                    "topic": msg.topic,
                    "partition": msg.partition,
                    "offset": msg.offset,
                    "normalized_event_id": str(data.get("normalized_event_id", "")),
                },
            )
        )

    async def process_message(self, data: dict) -> bool:
        try:
            event = EnrichedSecurityEvent(**data)
            alerts = await self.engine.evaluate_event(event)
            
            for alert in alerts:
                logger.warning(f"ALERT GENERATED: {alert.title} (Rule: {alert.rule_id})")
                try:
                    alert_id = await self.persistence.persist_alert(alert)
                    await self.publisher.publish(alert.model_copy(update={"alert_id": alert_id}))
                except Exception as e:
                    logger.error(f"Failed to persist/publish alert {alert.detection_id}: {str(e)}")
                    raise
                    
            return True
        except ValidationError as exc:
            # Malformed data is terminal; publish a DLQ record before acknowledging.
            try:
                await self._publish_retry_exhausted(data, type("Message", (), {"topic": self.topic, "partition": -1, "offset": -1})(), 0)
                logger.warning("Malformed enriched event sent to DLQ: %s", str(exc)[:200])
                return True
            except Exception:
                logger.exception("Failed to publish malformed detection event to DLQ")
                return False
        except Exception:
            logger.exception("Detection processing failed")
            return False
