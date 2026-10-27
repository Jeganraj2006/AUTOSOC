from autosoc_schemas.events import RawSecurityEvent, NormalizedSecurityEvent
from .base import BaseParser
from ..utils import parse_utc_timestamp, validate_ip, validate_port

class SyntheticParser(BaseParser):
    @property
    def parser_name(self) -> str:
        return "synthetic_parser"

    @property
    def parser_version(self) -> str:
        return "1.0.0"

    def parse(self, raw_event: RawSecurityEvent) -> NormalizedSecurityEvent:
        event = self._create_base_event(raw_event)
        payload = self._parse_json_payload(raw_event.payload)

        # Basic synthetic mapping
        event.event_category = payload.get("category", "unknown")
        event.event_type = payload.get("type", "unknown")
        event.event_action = payload.get("action")
        event.event_outcome = payload.get("outcome", "unknown")
        
        # Identity
        event.username = payload.get("user")
        event.hostname = payload.get("host")
        
        # Network
        event.source_ip = validate_ip(payload.get("src_ip"))
        event.source_port = validate_port(payload.get("src_port"))
        event.destination_ip = validate_ip(payload.get("dst_ip"))
        event.destination_port = validate_port(payload.get("dst_port"))
        event.protocol = payload.get("protocol")
        
        # Process
        if "process" in payload:
            event.process_name = payload["process"].get("name")
            event.process_id = payload["process"].get("pid")
            event.command_line = payload["process"].get("cmdline")
            
        # File
        if "file" in payload:
            event.file_name = payload["file"].get("name")
            event.file_path = payload["file"].get("path")
            hashes = payload["file"].get("hashes")
            if isinstance(hashes, dict):
                # The canonical schema is Dict[str, str]. Reject nested/untyped
                # payload fragments rather than allowing telemetry to alter mapping.
                event.file_hashes = {
                    str(algorithm).upper(): value
                    for algorithm, value in hashes.items()
                    if isinstance(value, str)
                }
            elif hashes is not None:
                event.normalization_warnings.append("file.hashes was not an object")
            
        # Timestamp
        raw_ts = payload.get("timestamp")
        if raw_ts:
            dt, quality = parse_utc_timestamp(raw_ts)
            event.event_time = dt
            event.timestamp_quality = quality
        else:
            event.event_time = event.received_at
            event.timestamp_quality = "received_time_fallback"
            
        return event
