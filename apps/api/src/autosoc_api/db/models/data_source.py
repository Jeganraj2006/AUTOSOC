import enum
from datetime import datetime
from sqlalchemy import String, Boolean, Enum, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from autosoc_api.db.base import Base, TimestampMixin, UUIDMixin

class DataSourceType(str, enum.Enum):
    SYNTHETIC = "synthetic"
    HTTP_JSON = "http_json"
    LINUX_SYSLOG = "linux_syslog"
    NETWORK_FLOW = "network_flow"
    WINDOWS_EVENT = "windows_event"
    KUBERNETES_AUDIT = "kubernetes_audit"
    AWS_CLOUDTRAIL = "aws_cloudtrail"

class DataSourceHealth(str, enum.Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    INACTIVE = "inactive"
    DISABLED = "disabled"
    ERROR = "error"

class DataSource(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "data_sources"
    
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    source_type: Mapped[DataSourceType] = mapped_column(Enum(DataSourceType, name="datasource_type_enum"), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    environment: Mapped[str] = mapped_column(String(50), default="production", nullable=False)
    
    # Authentication (Hashed API Key)
    api_key_hash: Mapped[str | None] = mapped_column(String(255))
    secret_reference: Mapped[str | None] = mapped_column(String(255))
    
    # Health Tracking
    health_state: Mapped[DataSourceHealth] = mapped_column(Enum(DataSourceHealth, name="datasource_health_enum"), default=DataSourceHealth.UNKNOWN, nullable=False)
    last_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_successful_ingestion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_failure_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    @property
    def status(self) -> str:
        return self.health_state.value
