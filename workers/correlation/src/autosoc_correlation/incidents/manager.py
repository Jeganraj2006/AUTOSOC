"""Durable incident creation and update for the correlation worker."""

import os
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from autosoc_api.db.models.alert import Alert
from autosoc_api.db.models.attack import AttackTechnique, IncidentAttackMapping
from autosoc_api.db.models.audit_log import AuditLog
from autosoc_api.db.models.incident import Incident, IncidentSeverity, IncidentStatus
from autosoc_api.db.models.incident_alert import IncidentAlert
from autosoc_api.db.models.incident_event import IncidentEvent
from autosoc_api.db.models.incident_timeline import IncidentTimeline
from autosoc_correlation.rules.rule_models import CorrelationRule
from autosoc_schemas.events.incident import IncidentCreated, IncidentUpdated


_DATABASE_URL = os.environ.get("DATABASE_URL")
if not _DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required for the correlation worker")

_engine = create_async_engine(_DATABASE_URL, pool_pre_ping=True)
_sessions = async_sessionmaker(_engine, expire_on_commit=False)


class IncidentManager:
    @staticmethod
    async def create_incident(
        incident_id: str,
        alerts: list[dict[str, Any]],
        entity_id: str,
        new_score: float,
        rule: CorrelationRule,
    ) -> IncidentCreated:
        now = datetime.now(timezone.utc)
        incident_uuid = uuid.UUID(incident_id)
        async with _sessions() as session:
            incident = Incident(
                id=incident_uuid,
                title=f"Correlated Activity: {rule.name} on {entity_id}",
                description=rule.description,
                severity=IncidentSeverity(rule.severity.lower()),
                status=IncidentStatus.NEW,
                risk_score=new_score,
                first_seen=now,
                last_seen=now,
                alert_count=0,
                event_count=0,
                primary_entities=[{"type": "correlation_entity", "value": entity_id}],
                tags=["correlated", rule.id],
                correlation_rule_ids=[rule.id],
                candidate_mitre_references=rule.mitre_tactics,
            )
            session.add(incident)
            await session.flush()
            await IncidentManager._attach_evidence(session, incident, alerts, rule, new_score, now)
            session.add(
                AuditLog(
                    id=uuid.uuid4(),
                    actor_id="autosoc-correlation-worker",
                    actor_name="AutoSOC Correlation Worker",
                    actor_roles="system",
                    action="incident.created",
                    target_type="incident",
                    target_id=str(incident.id),
                    status="success",
                    metadata_json={"correlation_rule_id": rule.id, "risk_score": new_score},
                )
            )
            await session.commit()
            return IncidentManager._created_event(incident, now)

    @staticmethod
    async def update_incident(
        incident_id: str,
        alerts: list[dict[str, Any]],
        new_score: float,
        rule: CorrelationRule,
    ) -> IncidentUpdated | None:
        now = datetime.now(timezone.utc)
        async with _sessions() as session:
            incident = await session.get(Incident, uuid.UUID(incident_id))
            if incident is None:
                # Redis state can outlive a manually removed database record.
                raise RuntimeError(f"Active correlated incident {incident_id} no longer exists")
            evidence_changed = await IncidentManager._attach_evidence(
                session, incident, alerts, rule, new_score, now
            )
            if not evidence_changed:
                # A replay of an already-linked detection must not create an
                # audit/timeline entry or a duplicate downstream prediction.
                return None
            incident.status = IncidentStatus.INVESTIGATING
            incident.risk_score = max(float(incident.risk_score or 0), new_score)
            incident.last_seen = now
            existing_rule_ids = set(incident.correlation_rule_ids or [])
            incident.correlation_rule_ids = sorted(existing_rule_ids | {rule.id})
            session.add(
                AuditLog(
                    id=uuid.uuid4(),
                    actor_id="autosoc-correlation-worker",
                    actor_name="AutoSOC Correlation Worker",
                    actor_roles="system",
                    action="incident.updated",
                    target_type="incident",
                    target_id=str(incident.id),
                    status="success",
                    metadata_json={"correlation_rule_id": rule.id, "risk_score": incident.risk_score},
                )
            )
            await session.commit()
            return IncidentManager._updated_event(incident, now)

    @staticmethod
    async def _attach_evidence(session, incident, alerts, rule, score, now) -> bool:
        linked_alert_ids = set(
            (await session.execute(
                select(IncidentAlert.alert_id).where(IncidentAlert.incident_id == incident.id)
            )).scalars().all()
        )
        linked_event_ids = set(
            (await session.execute(
                select(IncidentEvent.event_id).where(IncidentEvent.incident_id == incident.id)
            )).scalars().all()
        )
        candidate_techniques: set[str] = set(incident.candidate_mitre_references or [])
        changed = False

        for alert_payload in alerts:
            alert_id = IncidentManager._uuid_or_none(alert_payload.get("alert_id"))
            if alert_id and alert_id not in linked_alert_ids:
                persisted_alert = await session.get(Alert, alert_id)
                if persisted_alert:
                    persisted_alert.incident_id = incident.id
                    session.add(IncidentAlert(
                        id=uuid.uuid4(),
                        incident_id=incident.id,
                        alert_id=alert_id,
                        linked_at=now,
                        correlation_reason=rule.description,
                        correlation_score=score,
                        correlation_rule_id=rule.id,
                    ))
                    linked_alert_ids.add(alert_id)
                    changed = True

            for event_id_raw in alert_payload.get("event_ids", []):
                event_id = IncidentManager._uuid_or_none(event_id_raw)
                if event_id and event_id not in linked_event_ids:
                    session.add(IncidentEvent(
                        id=uuid.uuid4(),
                        incident_id=incident.id,
                        event_id=event_id,
                        source_type="normalized_event",
                        evidence_role="correlated_detection",
                        linked_at=now,
                    ))
                    linked_event_ids.add(event_id)
                    changed = True

            prior_techniques = set(candidate_techniques)
            candidate_techniques.update(alert_payload.get("candidate_mitre_techniques") or [])
            changed = changed or candidate_techniques != prior_techniques

        incident.alert_count = len(linked_alert_ids)
        incident.event_count = len(linked_event_ids)
        incident.candidate_mitre_references = sorted(candidate_techniques)
        mappings_added = await IncidentManager._ensure_attack_mappings(
            session, incident, candidate_techniques, linked_alert_ids, linked_event_ids, now
        )
        changed = changed or mappings_added
        if changed:
            session.add(IncidentTimeline(
                id=uuid.uuid4(),
                incident_id=incident.id,
                event_type="correlated",
                timestamp=now,
                data={"rule_id": rule.id, "alert_count": incident.alert_count, "risk_score": incident.risk_score},
            ))
        return changed

    @staticmethod
    async def _ensure_attack_mappings(session, incident, techniques, alert_ids, event_ids, now) -> bool:
        existing = set(
            (await session.execute(
                select(AttackTechnique.external_id)
                .join(IncidentAttackMapping, IncidentAttackMapping.technique_id == AttackTechnique.id)
                .where(IncidentAttackMapping.incident_id == incident.id)
            )).scalars().all()
        )
        added = False
        for external_id in sorted(set(techniques) - existing):
            technique = (await session.execute(
                select(AttackTechnique).where(AttackTechnique.external_id == external_id)
            )).scalars().first()
            if technique is None:
                # The detection rule has already supplied this ATT&CK identifier.
                # Store a minimal catalog entry so prediction can link durable evidence.
                technique = AttackTechnique(
                    id=uuid.uuid4(),
                    external_id=external_id,
                    name=external_id,
                    description="ATT&CK technique referenced by an AutoSOC detection rule.",
                    attack_version="v14.1",
                    platforms=[],
                    revoked=False,
                )
                session.add(technique)
                await session.flush()
            session.add(IncidentAttackMapping(
                id=uuid.uuid4(),
                incident_id=incident.id,
                technique_id=technique.id,
                status="candidate",
                confidence="rule-derived",
                mapping_source="detection_rule",
                evidence_summary="Technique was supplied by a correlated detection rule.",
                source_alert_ids=[str(value) for value in sorted(alert_ids, key=str)],
                source_event_ids=[str(value) for value in sorted(event_ids, key=str)],
                # The legacy ATT&CK tables were created with TIMESTAMP (without
                # time zone), unlike the incident tables. Persist the same UTC
                # instant in their required naive representation.
                mapped_at=now.replace(tzinfo=None),
                mapped_by="autosoc-correlation-worker",
            ))
            added = True
        return added

    @staticmethod
    def _created_event(incident: Incident, now: datetime) -> IncidentCreated:
        return IncidentCreated(
            incident_id=incident.id,
            title=incident.title,
            status=incident.status.value,
            severity=incident.severity.value,
            risk_score=float(incident.risk_score or 0),
            alert_count=incident.alert_count,
            primary_entities=incident.primary_entities or [],
            updated_at=now,
        )

    @staticmethod
    def _updated_event(incident: Incident, now: datetime) -> IncidentUpdated:
        return IncidentUpdated(
            incident_id=incident.id,
            title=incident.title,
            status=incident.status.value,
            severity=incident.severity.value,
            risk_score=float(incident.risk_score or 0),
            alert_count=incident.alert_count,
            primary_entities=incident.primary_entities or [],
            updated_at=now,
        )

    @staticmethod
    def _uuid_or_none(value: object) -> uuid.UUID | None:
        try:
            return uuid.UUID(str(value)) if value else None
        except (TypeError, ValueError):
            return None
