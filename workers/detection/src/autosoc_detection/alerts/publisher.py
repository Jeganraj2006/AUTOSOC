import json
from aiokafka import AIOKafkaProducer
from autosoc_schemas.events.detection import DetectionResult

class AlertPublisher:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.topic = topic
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
