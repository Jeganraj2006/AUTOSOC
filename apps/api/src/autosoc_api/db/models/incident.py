from sqlalchemy import String, Enum, Float, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from autosoc_api.db.base import Base, TimestampMixin, UUIDMixin
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any

class IncidentSeverity(str, enum.Enum):
    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(str, enum.Enum):
    NEW = "new"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    AWAITING_APPROVAL = "awaiting_approval"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"
    FALSE_POSITIVE = "false_positive"

class Incident(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "incidents"
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(4000))
    severity: Mapped[IncidentSeverity] = mapped_column(Enum(IncidentSeverity, name="incident_severity_enum", create_type=False), nullable=False, index=True)
    status: Mapped[IncidentStatus] = mapped_column(Enum(IncidentStatus, name="incident_status_enum", create_type=False), default=IncidentStatus.NEW, nullable=False, index=True)
    
    risk_score: Mapped[float | None] = mapped_column(Float, default=0.0)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    alert_count: Mapped[int] = mapped_column(Integer, default=0)
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    
    primary_entities: Mapped[list | None] = mapped_column(JSON)
    tags: Mapped[list | None] = mapped_column(JSON)
    correlation_rule_ids: Mapped[list | None] = mapped_column(JSON)
    candidate_mitre_references: Mapped[list | None] = mapped_column(JSON)
    
    resolution_summary: Mapped[str | None] = mapped_column(String(4000))
    closure_reason: Mapped[str | None] = mapped_column(String(1000))
    false_positive_reason: Mapped[str | None] = mapped_column(String(1000))
    
    assignee_id: Mapped[str | None] = mapped_column(String(255), index=True)
    
    # Relationships
    alerts = relationship("IncidentAlert", back_populates="incident", cascade="all, delete-orphan")
    events = relationship("IncidentEvent", back_populates="incident", cascade="all, delete-orphan")
    notes = relationship("IncidentNote", back_populates="incident", cascade="all, delete-orphan")
    timeline = relationship("IncidentTimeline", back_populates="incident", cascade="all, delete-orphan")
    attack_mappings = relationship("IncidentAttackMapping", back_populates="incident", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="incident", cascade="all, delete-orphan")
    agent_executions = relationship("AgentExecution", back_populates="incident", cascade="all, delete-orphan")
