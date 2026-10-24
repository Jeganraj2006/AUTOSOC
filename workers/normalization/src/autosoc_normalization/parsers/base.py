import json
import uuid
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime, timezone
from autosoc_schemas.events import RawSecurityEvent, NormalizedSecurityEvent

class BaseParser(ABC):
    @property
    @abstractmethod
    def parser_name(self) -> str:
        pass

    @property
    @abstractmethod
    def parser_version(self) -> str:
        pass

    def _create_base_event(self, raw_event: RawSecurityEvent) -> NormalizedSecurityEvent:
        """
        Creates a basic NormalizedSecurityEvent with common metadata from the RawSecurityEvent.
        """
        return NormalizedSecurityEvent(
            event_id=raw_event.event_id,
            normalized_event_id=uuid.uuid4(),
            ingestion_id=raw_event.ingestion_id,
            source_id=raw_event.source_id,
            source_type=raw_event.source_type,
            schema_version=1,
            received_at=raw_event.received_at,
            normalized_at=datetime.now(timezone.utc),
            raw_event_reference=f"raw-events/{raw_event.source_type}/{raw_event.source_id}/{raw_event.event_id}.json",
            raw_payload_hash=raw_event.payload_hash,
            parser_name=self.parser_name,
            parser_version=self.parser_version,
            trace_id=raw_event.trace_id,
            request_id=raw_event.request_id,
            # Defaults to be overridden by subclasses
            event_category="unknown",
            event_type="unknown",
            event_outcome="unknown"
        )

    def _parse_json_payload(self, payload: str) -> dict:
        """Safely parse the JSON payload."""
        try:
            parsed = json.loads(payload)
            if not isinstance(parsed, dict):
                return {"_raw": parsed}
            return parsed
        except json.JSONDecodeError:
            return {}

    @abstractmethod
    def parse(self, raw_event: RawSecurityEvent) -> NormalizedSecurityEvent:
        """
        Takes a RawSecurityEvent and returns a canonical NormalizedSecurityEvent.
        Must handle exceptions safely inside or bubble up defined ParseError.
        """
        pass
