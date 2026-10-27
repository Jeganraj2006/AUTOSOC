import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from autosoc_schemas.events.detection import DetectionResult
from autosoc_api.db.models.alert import Alert, AlertSeverity, AlertStatus
from autosoc_api.db.models.audit_log import AuditLog

class AlertPersistence:
    def __init__(self, database_url: str):
        # We assume the database schemas are already managed by the API's alembic migrations
        self.engine = create_async_engine(database_url, pool_size=5, max_overflow=10)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def close(self):
        await self.engine.dispose()

    async def persist_alert(self, result: DetectionResult) -> uuid.UUID:
        """Persist a detection before it is published to the correlation topic.

        Detection rules use stable string IDs, whereas ``alerts.rule_id`` is a
        foreign key to optional UI rule metadata.  Store the stable ID in the
        evidence payload instead of violating that foreign key.
        """
        async with self.session_factory() as session:
            existing = await session.execute(
                select(Alert.id).where(Alert.detection_id == result.detection_id)
            )
            existing_alert_id = existing.scalar_one_or_none()
            if existing_alert_id is not None:
                return existing_alert_id

            severity = result.severity.lower()
            if severity not in ["low", "medium", "high", "critical"]:
                severity = "low"

            alert = Alert(
                id=uuid.uuid4(),
                title=result.title,
                description=result.description,
                severity=AlertSeverity(severity),
                status=AlertStatus.NEW,
                detection_id=result.detection_id,
                source_event_id=str(result.event_ids[0]) if result.event_ids else None,
                indicators_json={
                    "entities": [entity.model_dump() for entity in result.entities],
                    "detection_id": str(result.detection_id),
                    "rule_id": result.rule_id,
                    "rule_version": result.rule_version,
                    "candidate_mitre_techniques": result.candidate_mitre_techniques,
                },
            )
            session.add(alert)
            session.add(
                AuditLog(
                    id=uuid.uuid4(),
                    actor_id="autosoc-detection-worker",
                    actor_name="AutoSOC Detection Worker",
                    actor_roles="system",
                    action="alert.created",
                    target_type="alert",
                    target_id=str(alert.id),
                    status="success",
                    metadata_json={
                        "detection_id": str(result.detection_id),
                        "rule_id": result.rule_id,
                    },
                )
            )
            try:
                await session.commit()
            except IntegrityError:
                # Another retry or worker instance persisted the stable ID.
                await session.rollback()
                existing = await session.execute(
                    select(Alert.id).where(Alert.detection_id == result.detection_id)
                )
                return existing.scalar_one()
            return alert.id
