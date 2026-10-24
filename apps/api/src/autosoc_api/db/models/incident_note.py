from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from autosoc_api.db.base import Base, UUIDMixin, TimestampMixin
import uuid

class IncidentNote(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "incident_notes"
    
    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Relationships
    incident = relationship("Incident", back_populates="notes")
