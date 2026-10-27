import uuid
import datetime
from typing import List, Optional
from autosoc_detection.rules.models import RuleModel
from autosoc_schemas.events.normalized import NormalizedSecurityEvent
from autosoc_schemas.events.detection import DetectionResult, EntityRef

class AlertGenerator:
    @staticmethod
    def generate(rule: RuleModel, event: NormalizedSecurityEvent, related_events: List[NormalizedSecurityEvent] = None) -> DetectionResult:
        if related_events is None:
            related_events = []
            
        all_events = [event] + related_events
        event_ids = [e.normalized_event_id for e in all_events]
        source_ids = list(set([e.source_id for e in all_events]))

        # Entity extraction mapping
        entities = AlertGenerator._extract_entities(all_events)
        
        # Build explanation
        desc = rule.description
        if rule.threshold:
            desc = f"Threshold triggered: {rule.threshold.count} events observed in {rule.threshold.timeframe}s. {desc}"

        # A repeat delivery of the same normalized event must generate the
        # same detection identity. Persistence can therefore acknowledge a
        # replay without emitting duplicate alerts or incidents.
        detection_identity = f"{rule.rule_id}:{rule.version}:{','.join(sorted(str(event_id) for event_id in event_ids))}"
        return DetectionResult(
            detection_id=uuid.uuid5(uuid.NAMESPACE_URL, detection_identity),
            rule_id=rule.rule_id,
            rule_version=rule.version,
            rule_name=rule.name,
            rule_type=rule.rule_type,
            event_ids=event_ids,
            source_ids=source_ids,
            detected_at=datetime.datetime.now(datetime.timezone.utc),
            severity=rule.severity,
            confidence=0.9 if rule.rule_type == "match" else 0.8,
            title=f"Detection: {rule.name}",
            description=desc,
            evidence=[e.model_dump(exclude_none=True) for e in all_events],
            entities=entities,
            candidate_mitre_techniques=rule.candidate_mitre_techniques,
            recommended_investigation=rule.investigation_guidance,
            trace_id=event.trace_id
        )

    @staticmethod
    def _extract_entities(events: List[NormalizedSecurityEvent]) -> List[EntityRef]:
        extracted = []
        seen = set()
        
        def add_entity(type_: str, val: Optional[str]):
            entity_key = (type_, val)
            if val and entity_key not in seen:
                extracted.append(EntityRef(type=type_, value=val))
                seen.add(entity_key)

        for e in events:
            # Direction is material to correlation.  Keep the legacy generic
            # ``ip`` reference for existing consumers, but also publish the
            # explicit source/destination identities used by correlation
            # rules.  Without these, a source-IP rule treats the destination
            # as another candidate and can open a spurious incident.
            add_entity("source_ip", e.source_ip)
            add_entity("destination_ip", e.destination_ip)
            add_entity("ip", e.source_ip)
            add_entity("ip", e.destination_ip)
            add_entity("user", e.username)
            add_entity("host", e.hostname)
            add_entity("process", e.process_name)
            add_entity("file", e.file_path)
            add_entity("file_hash", e.file_hashes.get("SHA256"))
            
        return extracted
