from autosoc_schemas.events import RawSecurityEvent, NormalizedSecurityEvent
from .base import BaseParser
from ..utils import parse_utc_timestamp, validate_ip, validate_port

class HttpJsonParser(BaseParser):
    @property
    def parser_name(self) -> str:
        return "http_json_parser"

    @property
    def parser_version(self) -> str:
        return "1.0.0"

    def parse(self, raw_event: RawSecurityEvent) -> NormalizedSecurityEvent:
        event = self._create_base_event(raw_event)
        payload = self._parse_json_payload(raw_event.payload)

        if not payload or "_raw" in payload:
            event.normalization_warnings.append("Payload was not valid JSON")
            event.normalization_confidence = "low"
            return event

        event.event_category = "other"
        
        # Generic fields extraction
        event.username = payload.get("username") or payload.get("user")
        event.hostname = payload.get("hostname") or payload.get("host")
        event.event_action = payload.get("action")
        
        status = payload.get("status") or payload.get("outcome")
        if status:
            event.event_outcome = str(status).lower()
        
        event.source_ip = validate_ip(payload.get("src_ip") or payload.get("source_ip"))
        event.destination_ip = validate_ip(payload.get("dst_ip") or payload.get("destination_ip"))
        event.protocol = payload.get("protocol")

        raw_ts = payload.get("timestamp") or payload.get("time")
        if raw_ts:
            dt, quality = parse_utc_timestamp(raw_ts)
            event.event_time = dt
            event.timestamp_quality = quality
            if quality == "invalid":
                event.normalization_warnings.append("Invalid timestamp format")
        else:
            event.event_time = event.received_at
            event.timestamp_quality = "received_time_fallback"
            event.normalization_warnings.append("Missing timestamp field")

        # Record unmapped field count (simplistic heuristic)
        known_keys = {"username", "user", "hostname", "host", "action", "status", "outcome", "src_ip", "source_ip", "dst_ip", "destination_ip", "protocol", "timestamp", "time"}
        unmapped_keys = set(payload.keys()) - known_keys
        if unmapped_keys:
            event.normalization_warnings.append(f"Unmapped fields: {len(unmapped_keys)}")

        return event
