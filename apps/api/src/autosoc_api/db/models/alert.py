from sqlalchemy import String, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from autosoc_api.db.base import Base, TimestampMixin, UUIDMixin
import enum
import uuid
from typing import Optional

class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, enum.Enum):
    NEW = "new"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"

class Alert(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "alerts"
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000))
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity, name="alert_severity_enum"), nullable=False, index=True)
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus, name="alert_status_enum"), default=AlertStatus.NEW, nullable=False, index=True)
    detection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    
    # Context
    source_event_id: Mapped[str | None] = mapped_column(String(255))
    rule_id: Mapped[str | None] = mapped_column(ForeignKey("detection_rule_metadata.id"), index=True)
    
    # Extracted fields for fast lookup (e.g., attacker IP, target host)
    indicators_json: Mapped[dict | list | None] = mapped_column(JSON().with_variant(JSONB, 'postgresql'))
    
    incident_id: Mapped[Optional[str]] = mapped_column(ForeignKey("incidents.id"), index=True, nullable=True)
