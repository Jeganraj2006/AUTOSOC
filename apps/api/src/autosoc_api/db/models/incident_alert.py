from sqlalchemy import String, ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from autosoc_api.db.base import Base, UUIDMixin
import uuid

class IncidentAlert(Base, UUIDMixin):
    __tablename__ = "incident_alerts"
    
    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    linked_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    correlation_reason: Mapped[str | None] = mapped_column(String(1000))
    correlation_score: Mapped[float | None] = mapped_column(Float)
    correlation_rule_id: Mapped[str | None] = mapped_column(String(255))
    
    # Relationships
    incident = relationship("Incident", back_populates="alerts")
    alert = relationship("Alert")
