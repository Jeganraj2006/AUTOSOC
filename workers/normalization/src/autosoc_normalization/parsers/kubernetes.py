from autosoc_schemas.events import RawSecurityEvent, NormalizedSecurityEvent
from .base import BaseParser
from ..utils import parse_utc_timestamp, validate_ip, mask_sensitive_data

class KubernetesAuditParser(BaseParser):
    @property
    def parser_name(self) -> str:
        return "kubernetes_audit_parser"

    @property
    def parser_version(self) -> str:
        return "1.0.0"

    def parse(self, raw_event: RawSecurityEvent) -> NormalizedSecurityEvent:
        event = self._create_base_event(raw_event)
        event.event_category = "kubernetes"
        
        payload = self._parse_json_payload(raw_event.payload)
        if not payload or "_raw" in payload:
            event.normalization_warnings.append("K8s audit event not valid JSON")
            event.normalization_confidence = "low"
            return event
            
        # Example K8s Audit Log Mapping
        event.event_action = payload.get("verb")
        
        user_info = payload.get("user", {})
        event.username = user_info.get("username")
        
        # Check if service account
        if event.username and event.username.startswith("system:serviceaccount:"):
            parts = event.username.split(":")
            if len(parts) >= 4:
                event.service_account = parts[-1]
                event.namespace = parts[-2]
                
        # Source IPs
        src_ips = payload.get("sourceIPs", [])
        if src_ips and isinstance(src_ips, list):
            event.source_ip = validate_ip(src_ips[0])
            
        object_ref = payload.get("objectRef", {})
        event.resource_type = object_ref.get("resource")
        if not event.namespace:
            event.namespace = object_ref.get("namespace")
        event.resource_id = object_ref.get("name")
        event.api_operation = object_ref.get("apiGroup")
        
        response = payload.get("responseStatus", {})
        code = response.get("code")
        if code:
            try:
                code_int = int(code)
                if code_int < 400:
                    event.event_outcome = "success"
                else:
                    event.event_outcome = "failure"
            except ValueError:
                pass
                
        raw_ts = payload.get("requestReceivedTimestamp")
        if raw_ts:
            dt, quality = parse_utc_timestamp(raw_ts)
            event.event_time = dt
            event.timestamp_quality = quality
        else:
            event.event_time = event.received_at
            event.timestamp_quality = "received_time_fallback"
            
        # Ensure we don't store raw bearer tokens from the request object
        # The base NormalizedSecurityEvent doesn't store the raw payload, but we make sure 
        # any message or summary string is masked.
        if "requestURI" in payload:
            event.message = mask_sensitive_data(payload["requestURI"])
            
        return event
