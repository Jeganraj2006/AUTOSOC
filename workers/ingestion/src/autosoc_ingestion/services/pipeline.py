import logging
import json
import uuid
import hashlib
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from autosoc_schemas.events.raw import RawSecurityEvent, FailedSecurityEvent, IngestionStatus, IngestionResult
from autosoc_ingestion.publishers.redpanda import RedpandaPublisher
from autosoc_ingestion.archive.minio_archive import MinioArchiveService
from autosoc_ingestion.deduplication.redis_dedup import DeduplicationService
from autosoc_ingestion.services.health_tracker import HealthTrackerService
from autosoc_ingestion.metrics.prometheus import INGESTION_EVENTS_TOTAL, INGESTION_PAYLOAD_BYTES

logger = logging.getLogger("ingestion.pipeline")

class IngestionPipeline:
    def __init__(self, 
                 publisher: RedpandaPublisher, 
                 archive: MinioArchiveService, 
                 dedup: DeduplicationService,
                 health_tracker: HealthTrackerService,
                 collector_version: str = "0.1.0",
                 retry_max_attempts: int = 5,
                 retry_base_delay_seconds: float = 1.0,
                 retry_max_delay_seconds: float = 30.0):
        self.publisher = publisher
        self.archive = archive
        self.dedup = dedup
        self.health_tracker = health_tracker
        self.collector_version = collector_version
        self.retry_max_attempts = retry_max_attempts
        self.retry_base_delay_seconds = retry_base_delay_seconds
        self.retry_max_delay_seconds = retry_max_delay_seconds

    async def _retry(self, stage: str, operation):
        """Run a transient I/O operation with bounded exponential backoff."""
        last_error = None
        for attempt in range(1, self.retry_max_attempts + 1):
            try:
                await operation()
                return True, None, attempt
            except Exception as exc:
                last_error = exc
                if attempt == self.retry_max_attempts:
                    break
                delay = min(
                    self.retry_max_delay_seconds,
                    self.retry_base_delay_seconds * (2 ** (attempt - 1)),
                )
                logger.warning(
                    "ingestion_retry_scheduled stage=%s attempt=%s max_attempts=%s delay_seconds=%s error=%s",
                    stage, attempt, self.retry_max_attempts, delay, f"{type(exc).__name__}: {exc}"[:500],
                )
                await asyncio.sleep(delay)
        return False, last_error, self.retry_max_attempts

    async def _handle_failure(self, 
                              failure_stage: str, 
                              reason_code: str, 
                              description: str,
                              source_id: Optional[str] = None,
                              source_type: Optional[str] = None,
                              payload_hash: Optional[str] = None,
                              retryable: bool = False,
                              trace_id: Optional[str] = None,
                              ingestion_id: Optional[uuid.UUID] = None,
                              retry_count: int = 0):
        failed_event = FailedSecurityEvent(
            failure_id=uuid.uuid4(),
            ingestion_id=ingestion_id,
            source_id=source_id,
            source_type=source_type,
            received_at=datetime.now(timezone.utc),
            failure_stage=failure_stage,
            failure_reason_code=reason_code,
            failure_description=description,
            payload_hash=payload_hash,
            trace_id=trace_id,
            retryable=retryable,
            retry_count=retry_count,
        )
        try:
            await self.publisher.publish_failed_event(failed_event)
        except Exception as e:
            logger.error(f"CRITICAL: Failed to publish to DLQ: {e}")
            # If we can't even write to DLQ, we have to drop or block.
            # In sync HTTP, this will result in a 500/503 to the client.

    async def process_event(self, 
                            payload: str, 
                            source_id: str, 
                            source_name: str, 
                            source_type: str, 
                            content_type: str, 
                            ingestion_method: str,
                            ingestion_id: uuid.UUID,
                            trace_id: Optional[str] = None,
                            request_id: Optional[str] = None) -> IngestionStatus:
        """
        Process a single raw event through the pipeline.
        Returns the ingestion status.
        """
        event_id = uuid.uuid4()
        received_at = datetime.now(timezone.utc)
        payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()

        # 1. Validation (JSON structural check)
        if content_type == "application/json":
            try:
                json.loads(payload)
            except json.JSONDecodeError:
                await self._handle_failure(
                    failure_stage="validation",
                    reason_code="INVALID_JSON",
                    description="Payload is not valid JSON",
                    source_id=source_id,
                    source_type=source_type,
                    payload_hash=payload_hash,
                    trace_id=trace_id,
                    ingestion_id=ingestion_id
                )
                await self.health_tracker.update_source_health(source_id, "rejected")
                INGESTION_EVENTS_TOTAL.labels(source_type=source_type, status="rejected").inc()
                return IngestionStatus(event_id=event_id, status="rejected", error="Invalid JSON")

        INGESTION_PAYLOAD_BYTES.labels(source_type=source_type).observe(len(payload.encode('utf-8')))

        # 2. Deduplication
        is_duplicate = await self.dedup.is_duplicate(source_id, payload_hash)
        if is_duplicate:
            logger.info(f"Duplicate event suppressed: {payload_hash} from {source_id}")
            await self.health_tracker.update_source_health(source_id, "duplicate")
            INGESTION_EVENTS_TOTAL.labels(source_type=source_type, status="duplicate").inc()
            return IngestionStatus(event_id=event_id, status="duplicate", duplicate=True)

        # 3. Envelope Creation
        raw_event = RawSecurityEvent(
            event_id=event_id,
            ingestion_id=ingestion_id,
            source_id=source_id,
            source_type=source_type,
            source_name=source_name,
            received_at=received_at,
            content_type=content_type,
            payload=payload,
            payload_hash=payload_hash,
            ingestion_method=ingestion_method,
            collector_version=self.collector_version,
            trace_id=trace_id,
            request_id=request_id
        )

        # 4. Archival
        archived, archive_error, archive_attempts = await self._retry(
            "archive", lambda: self.archive.archive_event(raw_event)
        )
        if not archived:
            # MinIO failure is transient.
            await self._handle_failure(
                failure_stage="archive",
                reason_code="ARCHIVE_FAILED",
                description=str(archive_error),
                source_id=source_id,
                source_type=source_type,
                payload_hash=payload_hash,
                retryable=True,
                trace_id=trace_id,
                ingestion_id=ingestion_id,
                retry_count=archive_attempts,
            )
            await self.dedup.release(source_id, payload_hash)
            # Fail the request so the source retries
            await self.health_tracker.update_source_health(source_id, "failed")
            INGESTION_EVENTS_TOTAL.labels(source_type=source_type, status="failed").inc()
            return IngestionStatus(event_id=event_id, status="failed", error="Archive timeout/failure")

        # 5. Publish to Redpanda
        published, publish_error, publish_attempts = await self._retry(
            "publish", lambda: self.publisher.publish_raw_event(raw_event)
        )
        if not published:
            await self._handle_failure(
                failure_stage="publish",
                reason_code="PUBLISH_FAILED",
                description=str(publish_error),
                source_id=source_id,
                source_type=source_type,
                payload_hash=payload_hash,
                retryable=True,
                trace_id=trace_id,
                ingestion_id=ingestion_id,
                retry_count=publish_attempts,
            )
            await self.dedup.release(source_id, payload_hash)
            await self.health_tracker.update_source_health(source_id, "failed")
            INGESTION_EVENTS_TOTAL.labels(source_type=source_type, status="failed").inc()
            return IngestionStatus(event_id=event_id, status="failed", error="Broker timeout/failure")

        await self.health_tracker.update_source_health(source_id, "accepted")
        INGESTION_EVENTS_TOTAL.labels(source_type=source_type, status="accepted").inc()
        return IngestionStatus(event_id=event_id, status="accepted")
