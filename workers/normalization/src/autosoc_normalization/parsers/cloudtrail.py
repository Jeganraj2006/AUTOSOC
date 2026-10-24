from autosoc_schemas.events import RawSecurityEvent, NormalizedSecurityEvent
from .base import BaseParser
from ..utils import parse_utc_timestamp, validate_ip, mask_sensitive_data

class CloudTrailParser(BaseParser):
    @property
    def parser_name(self) -> str:
        return "cloudtrail_parser"

    @property
    def parser_version(self) -> str:
        return "1.0.0"

    def parse(self, raw_event: RawSecurityEvent) -> NormalizedSecurityEvent:
        event = self._create_base_event(raw_event)
        event.event_category = "cloud"
        
        payload = self._parse_json_payload(raw_event.payload)
        if not payload or "_raw" in payload:
            event.normalization_warnings.append("CloudTrail event not valid JSON")
            event.normalization_confidence = "low"
            return event
            
        event.cloud_provider = "aws"
        event.cloud_account_id = payload.get("recipientAccountId")
        event.cloud_region = payload.get("awsRegion")
        event.api_operation = payload.get("eventName")
        event.event_action = payload.get("eventName")
        
        # Identity
        user_identity = payload.get("userIdentity", {})
        event.username = user_identity.get("userName") or user_identity.get("arn")
        event.user_id = user_identity.get("principalId")
        event.user_type = user_identity.get("type")
        
        # Source IP
        src_ip = payload.get("sourceIPAddress")
        if src_ip:
            # AWS sometimes sets this to things like "cloudformation.amazonaws.com"
            validated = validate_ip(src_ip)
            if validated:
                event.source_ip = validated
            else:
                event.hostname = src_ip # Treat as hostname if not IP
                
        # Outcome
        if payload.get("errorCode") or payload.get("errorMessage"):
            event.event_outcome = "failure"
            event.failure_reason = mask_sensitive_data(payload.get("errorCode", "unknown error"))
        else:
            event.event_outcome = "success"
            
        raw_ts = payload.get("eventTime")
        if raw_ts:
            dt, quality = parse_utc_timestamp(raw_ts)
            event.event_time = dt
            event.timestamp_quality = quality
        else:
            event.event_time = event.received_at
            event.timestamp_quality = "received_time_fallback"
            
        event.request_id = payload.get("requestID")
        
        # Resources (simplistic mapping of the first resource)
        resources = payload.get("resources", [])
        if resources and isinstance(resources, list) and len(resources) > 0:
            event.resource_type = resources[0].get("type")
            event.resource_id = resources[0].get("ARN") or resources[0].get("accountId")
            
        return event
