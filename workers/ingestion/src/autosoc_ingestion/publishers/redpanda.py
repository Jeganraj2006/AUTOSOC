import logging
import json
import asyncio
from aiokafka import AIOKafkaProducer
from autosoc_schemas.events.raw import RawSecurityEvent, FailedSecurityEvent
from typing import Optional

logger = logging.getLogger("ingestion.publisher.redpanda")

class RedpandaPublisher:
    def __init__(self, bootstrap_servers: str, raw_topic: str = "security.events.raw", failed_topic: str = "security.events.failed"):
        self.bootstrap_servers = bootstrap_servers
        self.raw_topic = raw_topic
        self.failed_topic = failed_topic
        self.producer: Optional[AIOKafkaProducer] = None

    async def connect(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            client_id="ingestion_worker",
            request_timeout_ms=5000,
            retry_backoff_ms=100,
            # Idempotent producer config (Phase 6 requirement)
            enable_idempotence=True, 
            acks="all"
        )
        await self.producer.start()
        logger.info(f"Connected to Redpanda at {self.bootstrap_servers}")

    async def disconnect(self):
        if self.producer:
            await self.producer.stop()
            logger.info("Disconnected from Redpanda")

    async def publish_raw_event(self, event: RawSecurityEvent) -> bool:
        if not self.producer:
            raise RuntimeError("Producer not initialized. Call connect() first.")
            
        payload = event.model_dump_json().encode("utf-8")
        # Use source_id as the routing key to guarantee ordering per data source
        key = event.source_id.encode("utf-8")
        headers = [
            ("trace_id", event.trace_id.encode("utf-8") if event.trace_id else b""),
            ("schema_version", str(event.schema_version).encode("utf-8"))
        ]
        
        try:
            # Send and wait for ack
            await self.producer.send_and_wait(
                topic=self.raw_topic,
                value=payload,
                key=key,
                headers=headers
            )
            return True
        except Exception as e:
            logger.error(f"Failed to publish raw event {event.event_id} to {self.raw_topic}: {e}")
            raise # Let caller handle retry

    async def publish_failed_event(self, event: FailedSecurityEvent) -> bool:
        if not self.producer:
            raise RuntimeError("Producer not initialized. Call connect() first.")
            
        payload = event.model_dump_json().encode("utf-8")
        key = str(event.failure_id).encode("utf-8")
        headers = [
            ("trace_id", event.trace_id.encode("utf-8") if event.trace_id else b""),
            ("schema_version", str(event.schema_version).encode("utf-8"))
        ]
        
        try:
            await self.producer.send_and_wait(
                topic=self.failed_topic,
                value=payload,
                key=key,
                headers=headers
            )
            return True
        except Exception as e:
            logger.error(f"Failed to publish dead-letter event {event.failure_id} to {self.failed_topic}: {e}")
            raise
