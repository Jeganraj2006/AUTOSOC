from autosoc_schemas.events import RawSecurityEvent, NormalizedSecurityEvent
from .base import BaseParser
from ..utils import parse_utc_timestamp, validate_ip, validate_port

class NetworkFlowParser(BaseParser):
    @property
    def parser_name(self) -> str:
        return "network_flow_parser"

    @property
    def parser_version(self) -> str:
        return "1.0.0"

    def parse(self, raw_event: RawSecurityEvent) -> NormalizedSecurityEvent:
        event = self._create_base_event(raw_event)
        event.event_category = "network"
        event.event_type = "flow"
        
        payload = self._parse_json_payload(raw_event.payload)
        
        if not payload or "_raw" in payload:
            event.normalization_warnings.append("Flow event not valid JSON")
            event.normalization_confidence = "low"
            return event
            
        # E.g., NetFlow V9 / IPFIX common structure JSON
        event.source_ip = validate_ip(payload.get("src_ip"))
        event.destination_ip = validate_ip(payload.get("dst_ip"))
        event.source_port = validate_port(payload.get("src_port"))
        event.destination_port = validate_port(payload.get("dst_port"))
        event.protocol = str(payload.get("protocol", ""))
        
        if not event.source_ip or not event.destination_ip:
            event.normalization_warnings.append("Missing valid IPs")
            event.normalization_confidence = "low"
            
        try:
            bytes_in = int(payload.get("bytes_in", 0))
            bytes_out = int(payload.get("bytes_out", 0))
            if bytes_in < 0 or bytes_out < 0:
                raise ValueError
            event.bytes_in = bytes_in
            event.bytes_out = bytes_out
        except (ValueError, TypeError):
            event.normalization_warnings.append("Invalid byte counts")
            
        try:
            pkts_in = int(payload.get("packets_in", 0))
            pkts_out = int(payload.get("packets_out", 0))
            if pkts_in < 0 or pkts_out < 0:
                raise ValueError
            event.packets_in = pkts_in
            event.packets_out = pkts_out
        except (ValueError, TypeError):
            event.normalization_warnings.append("Invalid packet counts")
            
        try:
            duration = int(payload.get("duration", 0))
            if duration < 0:
                raise ValueError
            event.session_duration = duration
        except (ValueError, TypeError):
            event.normalization_warnings.append("Invalid duration")
            
        raw_ts = payload.get("timestamp")
        if raw_ts:
            dt, quality = parse_utc_timestamp(raw_ts)
            event.event_time = dt
            event.timestamp_quality = quality
        else:
            event.event_time = event.received_at
            event.timestamp_quality = "received_time_fallback"
            
        return event
