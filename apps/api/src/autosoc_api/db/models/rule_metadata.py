import enum
from sqlalchemy import String, Boolean, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column
from autosoc_api.db.base import Base, TimestampMixin, UUIDMixin

class RuleSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DetectionRuleMetadata(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "detection_rule_metadata"
    
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    severity: Mapped[RuleSeverity] = mapped_column(Enum(RuleSeverity, name="rule_severity_enum"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    mitre_references_json: Mapped[str | None] = mapped_column(String(1000)) # Placeholder for MITRE
    file_path: Mapped[str | None] = mapped_column(String(500))
