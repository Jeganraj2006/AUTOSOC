import pytest
import uuid
import json
from unittest.mock import AsyncMock, MagicMock
from autosoc_ingestion.services.pipeline import IngestionPipeline
from autosoc_schemas.events.raw import RawSecurityEvent, FailedSecurityEvent

@pytest.fixture
def mocks():
    publisher = AsyncMock()
    archive = AsyncMock()
    dedup = AsyncMock()
    health = AsyncMock()
    return publisher, archive, dedup, health

@pytest.mark.asyncio
async def test_valid_json_ingestion(mocks):
    publisher, archive, dedup, health = mocks
    dedup.is_duplicate.return_value = False
    
    pipeline = IngestionPipeline(publisher, archive, dedup, health)
    
    payload = json.dumps({"test": "data", "user": "admin"})
    
    status = await pipeline.process_event(
        payload=payload,
        source_id="src-123",
        source_name="Test Source",
        source_type="http_json",
        content_type="application/json",
        ingestion_method="http",
        ingestion_id=uuid.uuid4()
    )
    
    assert status.status == "accepted"
    archive.archive_event.assert_called_once()
    publisher.publish_raw_event.assert_called_once()
    health.update_source_health.assert_called_with("src-123", "accepted")

@pytest.mark.asyncio
async def test_invalid_json_rejected(mocks):
    publisher, archive, dedup, health = mocks
    dedup.is_duplicate.return_value = False
    
    pipeline = IngestionPipeline(publisher, archive, dedup, health)
    
    status = await pipeline.process_event(
        payload="not valid json",
        source_id="src-123",
        source_name="Test Source",
        source_type="http_json",
        content_type="application/json",
        ingestion_method="http",
        ingestion_id=uuid.uuid4()
    )
    
    assert status.status == "rejected"
    assert status.error == "Invalid JSON"
    # Should publish to DLQ
    publisher.publish_failed_event.assert_called_once()
    archive.archive_event.assert_not_called()
    health.update_source_health.assert_called_with("src-123", "rejected")

@pytest.mark.asyncio
async def test_duplicate_suppression(mocks):
    publisher, archive, dedup, health = mocks
    dedup.is_duplicate.return_value = True
    
    pipeline = IngestionPipeline(publisher, archive, dedup, health)
    
    status = await pipeline.process_event(
        payload='{"test": "data"}',
        source_id="src-123",
        source_name="Test Source",
        source_type="http_json",
        content_type="application/json",
        ingestion_method="http",
        ingestion_id=uuid.uuid4()
    )
    
    assert status.status == "duplicate"
    assert status.duplicate is True
    publisher.publish_raw_event.assert_not_called()
    health.update_source_health.assert_called_with("src-123", "duplicate")

@pytest.mark.asyncio
async def test_archive_failure_triggers_retryable_error(mocks):
    publisher, archive, dedup, health = mocks
    dedup.is_duplicate.return_value = False
    archive.archive_event.side_effect = Exception("MinIO timeout")
    
    pipeline = IngestionPipeline(publisher, archive, dedup, health)
    
    status = await pipeline.process_event(
        payload='{"test": "data"}',
        source_id="src-123",
        source_name="Test Source",
        source_type="http_json",
        content_type="application/json",
        ingestion_method="http",
        ingestion_id=uuid.uuid4()
    )
    
    assert status.status == "failed"
    assert status.error == "Archive timeout/failure"
    
    # Should publish to DLQ with retryable=True
    publisher.publish_failed_event.assert_called_once()
    call_args = publisher.publish_failed_event.call_args[0][0]
    assert call_args.retryable is True
    assert call_args.failure_stage == "archive"
    
    health.update_source_health.assert_called_with("src-123", "failed")
