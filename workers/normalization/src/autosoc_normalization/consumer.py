import json
import logging
import uuid
import asyncio
from datetime import datetime, timezone
from aiokafka import AIOKafkaConsumer
from autosoc_schemas.events import RawSecurityEvent, FailedSecurityEvent
from autosoc_api.services.worker_reliability import RedisRetryState
from .config import settings
from .registry import parser_registry
from .enrichment.modules import EnrichmentEngine
from .publisher import EventPublisher
from .storage.opensearch import OpenSearchStorage

logger = logging.getLogger(__name__)

class NormalizationConsumer:
    def __init__(
        self,
        publisher: EventPublisher,
        opensearch: OpenSearchStorage,
        retry_state: RedisRetryState,
    ):
        self.publisher = publisher
        self.opensearch = opensearch
        self.enrichment_engine = EnrichmentEngine()
        self.retry_state = retry_state
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
                message_key = self.retry_state.message_key(
                    msg.topic, msg.partition, msg.offset
                )
                while self.running:
                    processed = await self.process_message(msg)
                    if processed:
                        await self.retry_state.acknowledge(message_key)
                        await self.consumer.commit()
                        break

                    decision = await self.retry_state.record_failure(
                        message_key,
                        RuntimeError("normalization pipeline was not durable"),
                    )
                    if decision.exhausted:
                        try:
                            await self._handle_failure(
                                self._raw_event_from_message(msg),
                                "normalization",
                                "RETRY_EXHAUSTED",
                                "Normalization failed after bounded retries",
                                retryable=False,
                                retry_count=decision.attempt,
                                safe_metadata={
                                    "topic": msg.topic,
                                    "partition": msg.partition,
                                    "offset": msg.offset,
                                },
                            )
                        except Exception:
                            logger.exception("DLQ publish failed; retaining Kafka offset")
                            await asyncio.sleep(decision.delay_seconds)
                            continue
                        logger.error(
                            "Retry exhausted for normalization message %s; published to DLQ",
                            message_key,
                        )
                        await self.retry_state.acknowledge(message_key)
                        await self.consumer.commit()
                        break
                    await asyncio.sleep(decision.delay_seconds)
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("Normalization consumer loop stopped unexpectedly")
        finally:
            await self.consumer.stop()

    async def stop(self):
        self.running = False

    @staticmethod
    def _raw_event_from_message(msg):
        try:
            return RawSecurityEvent(**msg.value)
        except Exception:
            return None

    async def process_message(self, msg) -> bool:
        raw_event = None
        try:
            raw_event = RawSecurityEvent(**msg.value)
        except Exception as e:
            logger.error(f"Failed to deserialize RawSecurityEvent: {e}")
            try:
                await self._handle_failure(None, "deserialization", "VALIDATION_ERROR", str(e), msg.value)
                return True
            except Exception:
                logger.exception("Unable to publish normalization validation failure")
                return False

        parser = parser_registry.get_parser(raw_event.source_type)
        if not parser:
            logger.warning(f"No parser found for source_type: {raw_event.source_type}")
            try:
                await self._handle_failure(raw_event, "normalization", "MISSING_PARSER", "No parser registered")
                return True
            except Exception:
                logger.exception("Unable to publish missing-parser failure")
                return False

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
                raise RuntimeError(f"OpenSearch indexing failed for {enriched.event_id}")
            return True

        except Exception:
            logger.exception("Normalization pipeline failed for %s", raw_event.event_id)
            return False

    async def _handle_failure(
        self,
        raw_event,
        stage,
        code,
        desc,
        raw_payload=None,
        *,
        retryable=False,
        retry_count=0,
        safe_metadata=None,
    ):
        failure = FailedSecurityEvent(
            failure_id=uuid.uuid4(),
            ingestion_id=raw_event.ingestion_id if raw_event else None,
            source_id=raw_event.source_id if raw_event else None,
            source_type=raw_event.source_type if raw_event else None,
            received_at=datetime.now(timezone.utc),
            failure_stage=stage,
            failure_reason_code=code,
            failure_description=desc[:1_000],
            payload_hash=raw_event.payload_hash if raw_event else None,
            trace_id=raw_event.trace_id if raw_event else None,
            retryable=retryable,
            retry_count=retry_count,
            safe_metadata=safe_metadata or {},
        )
        await self.publisher.publish_failure(failure)
