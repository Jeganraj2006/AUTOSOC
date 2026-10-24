from sqlalchemy import String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from autosoc_api.db.base import Base, UUIDMixin
import uuid
from datetime import datetime

class IncidentTimeline(Base, UUIDMixin):
    __tablename__ = "incident_timeline"
    
    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    data: Mapped[dict | None] = mapped_column(JSON)
    
    # Relationships
    incident = relationship("Incident", back_populates="timeline")
