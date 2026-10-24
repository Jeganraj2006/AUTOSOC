import re
from autosoc_schemas.events import RawSecurityEvent, NormalizedSecurityEvent
from .base import BaseParser
from ..utils import parse_utc_timestamp, validate_ip

class SyslogParser(BaseParser):
    @property
    def parser_name(self) -> str:
        return "syslog_parser"

    @property
    def parser_version(self) -> str:
        return "1.0.0"
        
    def parse(self, raw_event: RawSecurityEvent) -> NormalizedSecurityEvent:
        event = self._create_base_event(raw_event)
        event.event_category = "system"
        
        payload = raw_event.payload.strip()
        
        # Extremely basic RFC3164 / RFC5424 regex heuristic
        # e.g., <34>Oct 11 22:14:15 mymachine su: 'su root' failed for lonvick on /dev/pts/8
        rfc3164_pattern = re.compile(r'^<(\d+)>([A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+([^:]+):\s+(.*)$')
        
        match = rfc3164_pattern.match(payload)
        if match:
            pri, ts_str, host, app, msg = match.groups()
            
            # Pri parsing
            pri_int = int(pri)
            facility = pri_int >> 3
            severity = pri_int & 7
            event.severity_source = str(severity)
            
            event.hostname = host
            event.process_name = app.split('[')[0] if '[' in app else app
            event.message = msg
            
            # Timestamp (Note: Syslog 3164 lacks year, which is a known issue. Fallback to current year for MVP)
            # A real parser would inject the current year
            event.event_time = event.received_at
            event.timestamp_quality = "received_time_fallback"
            event.normalization_warnings.append("Syslog RFC3164 timestamp lacks year; using received_time_fallback")
            
            # Extract common auth logs
            if "failed" in msg.lower() or "invalid" in msg.lower():
                event.event_outcome = "failure"
                if "authentication" in msg.lower() or "password" in msg.lower():
                    event.event_category = "authentication"
            
        else:
            event.message = payload
            event.normalization_warnings.append("Failed to match RFC3164 Syslog format")
            event.normalization_confidence = "low"
            event.event_time = event.received_at
            event.timestamp_quality = "received_time_fallback"
            
        return event
