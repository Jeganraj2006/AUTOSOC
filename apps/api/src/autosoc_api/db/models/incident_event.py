from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from autosoc_api.db.base import Base, UUIDMixin
import uuid

class IncidentEvent(Base, UUIDMixin):
    __tablename__ = "incident_events"
    
    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True) # UUID for normalized event
    
    source_type: Mapped[str] = mapped_column(String(50), default="normalized_event")
    evidence_role: Mapped[str | None] = mapped_column(String(255))
    linked_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    incident = relationship("Incident", back_populates="events")
