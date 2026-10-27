import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from autosoc_schemas.events.detection import DetectionResult
from autosoc_schemas.events.raw import FailedSecurityEvent
from autosoc_api.services.worker_reliability import RedisRetryState

from autosoc_correlation.engine.correlator import correlate_alert

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("autosoc_correlation.main")

# Kept as a compatibility symbol for code importing the prior FastKafka app.
app = None


class CorrelationWorker:
    def __init__(self, _legacy_app=None):
        import os

        self.bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
        self.topic = os.environ.get("KAFKA_ALERT_TOPIC", "security.alerts")
        self.incidents_topic = os.environ.get("INCIDENTS_TOPIC", "security.incidents")
        self.group_id = os.environ.get("KAFKA_CONSUMER_GROUP", "autosoc-correlation-worker")
        self.retry_state = RedisRetryState(
            os.environ.get("REDIS_URL", "redis://redis:6379/2"),
            "correlation",
            max_attempts=int(os.environ.get("RETRY_MAX_ATTEMPTS", "5")),
            base_delay_seconds=float(os.environ.get("RETRY_BASE_DELAY_SECONDS", "1")),
            max_delay_seconds=float(os.environ.get("RETRY_MAX_DELAY_SECONDS", "30")),
        )
        self._running = False
        self._consumer = None
        self._producer = None

    async def run(self):
        self._consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset="latest",
            enable_auto_commit=False,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        )
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        )
        await self._consumer.start()
        await self._producer.start()
        self._running = True
        logger.info("Correlation worker is consuming %s", self.topic)
        try:
            async for message in self._consumer:
                message_key = self.retry_state.message_key(
                    message.topic, message.partition, message.offset
                )
                while self._running:
                    try:
                        events = await correlate_alert(DetectionResult(**message.value))
                        for event in events:
                            await self._producer.send_and_wait(
                                self.incidents_topic, event.model_dump(mode="json")
                            )
                            logger.info("Published %s event for incident %s", event.operation_type, event.incident_id)
                    except Exception as exc:
                        decision = await self.retry_state.record_failure(message_key, exc)
                        if decision.exhausted:
                            try:
                                await self._publish_retry_exhausted(message, decision.attempt)
                            except Exception:
                                logger.exception("Correlation DLQ publish failed; retaining Kafka offset")
                                await asyncio.sleep(decision.delay_seconds)
                                continue
                            logger.error("Retry exhausted for correlation message %s", message_key)
                            await self.retry_state.acknowledge(message_key)
                            await self._consumer.commit()
                            break
                        await asyncio.sleep(decision.delay_seconds)
                        continue
                    await self.retry_state.acknowledge(message_key)
                    await self._consumer.commit()
                    break
                if not self._running:
                    break
        finally:
            self._running = False
            if self._consumer:
                await self._consumer.stop()
            if self._producer:
                await self._producer.stop()
            await self.retry_state.close()

    async def _publish_retry_exhausted(self, message, retry_count: int) -> None:
        payload = message.value if isinstance(message.value, dict) else {}
        failure = FailedSecurityEvent(
            failure_id=uuid.uuid4(),
            source_id=None,
            source_type="detection_result",
            received_at=datetime.now(timezone.utc),
            failure_stage="correlation",
            failure_reason_code="RETRY_EXHAUSTED",
            failure_description="Correlation failed after bounded retries",
            trace_id=payload.get("trace_id"),
            retryable=False,
            retry_count=retry_count,
            safe_metadata={
                "topic": message.topic,
                "partition": message.partition,
                "offset": message.offset,
                "detection_id": str(payload.get("detection_id", "")),
            },
        )
        await self._producer.send_and_wait(
            "security.events.failed", failure.model_dump(mode="json"), key=str(failure.failure_id).encode()
        )

    async def stop(self):
        self._running = False


async def main():
    worker = CorrelationWorker()
    await worker.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("AutoSOC Correlation Worker shutting down")
