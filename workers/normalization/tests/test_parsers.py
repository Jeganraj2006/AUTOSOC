import pytest
import uuid
from datetime import datetime, timezone
from autosoc_schemas.events import RawSecurityEvent
from autosoc_normalization.parsers import SyntheticParser

def test_synthetic_parser():
    parser = SyntheticParser()
    raw_event = RawSecurityEvent(
        event_id=uuid.uuid4(),
        ingestion_id=uuid.uuid4(),
        source_id="test-source",
        source_type="synthetic",
        source_name="Synthetic Source",
        received_at=datetime.now(timezone.utc),
        content_type="application/json",
        payload='{"category": "authentication", "type": "login", "outcome": "success", "src_ip": "10.0.0.1"}',
        payload_hash="testhash",
        ingestion_method="http",
        collector_version="1.0"
    )
    
    normalized = parser.parse(raw_event)
    assert normalized.event_category == "authentication"
    assert normalized.event_type == "login"
    assert normalized.event_outcome == "success"
    assert normalized.source_ip == "10.0.0.1"
    assert normalized.schema_version == 1


def test_synthetic_parser_preserves_string_file_hashes():
    parser = SyntheticParser()
    raw_event = RawSecurityEvent(
        event_id=uuid.uuid4(),
        ingestion_id=uuid.uuid4(),
        source_id="test-source",
        source_type="synthetic",
        source_name="Synthetic Source",
        received_at=datetime.now(timezone.utc),
        content_type="application/json",
        payload=(
            '{"category":"file","type":"create",'
            '"file":{"name":"sample.bin","hashes":'
            '{"sha256":"abc123","md5":"def456","invalid":3}}}'
        ),
        payload_hash="testhash",
        ingestion_method="http",
        collector_version="1.0",
    )

    normalized = parser.parse(raw_event)

    assert normalized.file_hashes == {"SHA256": "abc123", "MD5": "def456"}
