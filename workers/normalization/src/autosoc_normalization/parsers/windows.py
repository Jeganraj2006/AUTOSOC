from autosoc_schemas.events import RawSecurityEvent, NormalizedSecurityEvent
from .base import BaseParser
from ..utils import parse_utc_timestamp, validate_ip, validate_port

class WindowsEventParser(BaseParser):
    @property
    def parser_name(self) -> str:
        return "windows_event_parser"

    @property
    def parser_version(self) -> str:
        return "1.0.0"

    def parse(self, raw_event: RawSecurityEvent) -> NormalizedSecurityEvent:
        event = self._create_base_event(raw_event)
        payload = self._parse_json_payload(raw_event.payload)

        if not payload or "_raw" in payload:
            event.normalization_warnings.append("Windows event not valid JSON")
            event.normalization_confidence = "low"
            return event

        event.event_category = "system"
        
        system = payload.get("System", {})
        event_data = payload.get("EventData", {})
        
        event_id = system.get("EventID")
        if event_id:
            event.event_type = f"windows_{event_id}"
            
        provider = system.get("Provider", {}).get("Name")
        event.hostname = system.get("Computer")
        
        raw_ts = system.get("TimeCreated", {}).get("SystemTime")
        if raw_ts:
            dt, quality = parse_utc_timestamp(raw_ts)
            event.event_time = dt
            event.timestamp_quality = quality
        else:
            event.event_time = event.received_at
            event.timestamp_quality = "received_time_fallback"
            
        # Common Windows Event Fields Mapping
        # E.g., 4624 Successful Logon
        if event_id in [4624, 4625]:
            event.event_category = "authentication"
            event.event_outcome = "success" if event_id == 4624 else "failure"
            event.username = event_data.get("TargetUserName")
            event.user_domain = event_data.get("TargetDomainName")
            event.source_ip = validate_ip(event_data.get("IpAddress"))
            event.source_port = validate_port(event_data.get("IpPort"))
            event.authentication_method = event_data.get("LogonType")
            
        # Process Creation (4688)
        elif event_id == 4688:
            event.event_category = "process"
            event.username = event_data.get("SubjectUserName")
            event.process_name = event_data.get("NewProcessName")
            event.command_line = event_data.get("CommandLine")
            # PPID requires conversion from hex string in many windows event formats
            
        return event
