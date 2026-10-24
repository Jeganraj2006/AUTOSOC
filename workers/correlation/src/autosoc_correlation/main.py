import logging
import asyncio
from typing import Dict, Any

from fastkafka import FastKafka
from autosoc_schemas.events.detection import DetectionResult
from autosoc_correlation.consumer import setup_consumer
from autosoc_correlation.publisher import setup_publisher

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("autosoc_correlation.main")

# We mock Kafka connection handling similarly to detection worker
app = FastKafka(
    kafka_brokers={"localhost": {"url": "redpanda", "port": 9092, "description": "Local Redpanda broker"}},
)

setup_consumer(app)
publish_incident = setup_publisher(app)

class CorrelationWorker:
    def __init__(self, fastkafka_app: FastKafka):
        self.app = fastkafka_app
        self._running = False

    async def run(self):
        self._running = True
        logger.info("AutoSOC Correlation Worker Starting...")
        try:
            async with self.app:
                while self._running:
                    await asyncio.sleep(1)
        finally:
            self._running = False

    async def stop(self):
        self._running = False

async def main():
    worker = CorrelationWorker(app)
    try:
        await worker.run()
    except asyncio.CancelledError:
        pass
    finally:
        await worker.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("AutoSOC Correlation Worker shutting down...")
