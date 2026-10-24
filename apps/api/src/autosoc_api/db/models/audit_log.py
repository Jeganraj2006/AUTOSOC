from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from autosoc_api.db.base import Base, TimestampMixin, UUIDMixin

class AuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audit_logs"
    
    actor_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    actor_name: Mapped[str | None] = mapped_column(String(255))
    actor_roles: Mapped[str | None] = mapped_column(String(1000))
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False) # 'success', 'failure'
    request_id: Mapped[str | None] = mapped_column(String(36))
    source_ip: Mapped[str | None] = mapped_column(String(45))
    reason: Mapped[str | None] = mapped_column(Text)
    
    # Store arbitrary diffs or old/new state
    metadata_json: Mapped[dict | list | None] = mapped_column(JSON().with_variant(JSONB, 'postgresql'))
