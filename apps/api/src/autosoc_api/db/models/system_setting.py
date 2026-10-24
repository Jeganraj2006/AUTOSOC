from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from autosoc_api.db.base import Base, TimestampMixin, UUIDMixin

class SystemSetting(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "system_settings"
    
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    value: Mapped[str] = mapped_column(String(2000), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
