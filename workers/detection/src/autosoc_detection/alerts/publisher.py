import json
from aiokafka import AIOKafkaProducer
from autosoc_schemas.events.detection import DetectionResult
from autosoc_schemas.events.raw import FailedSecurityEvent

class AlertPublisher:
    def __init__(self, bootstrap_servers: str, topic: str, failed_topic: str = "security.events.failed"):
        self.topic = topic
        self.failed_topic = failed_topic
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )

    async def start(self):
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def publish(self, alert: DetectionResult):
        # We can dump using model_dump mode="json" in pydantic v2 to serialize UUID/datetime
        val = alert.model_dump(mode="json")
        await self.producer.send_and_wait(self.topic, val)

    async def publish_failure(self, failure: FailedSecurityEvent):
        await self.producer.send_and_wait(
            self.failed_topic,
            failure.model_dump(mode="json"),
            key=str(failure.failure_id).encode(),
        )
