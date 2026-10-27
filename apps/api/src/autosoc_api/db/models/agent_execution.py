from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from autosoc_api.db.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone

class AgentExecutionStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    BLOCKED_BY_POLICY = "blocked_by_policy"

class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_type = Column(String, default="full_investigation")
    status = Column(Enum(AgentExecutionStatus), default=AgentExecutionStatus.QUEUED, index=True)
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    requested_by = Column(String, nullable=True)
    
    current_step = Column(String, nullable=True)
    steps_completed = Column(Integer, default=0)
    retry_count = Column(Integer, default=0, nullable=False)
    node_statuses = Column(JSON, nullable=True)
    node_timestamps = Column(JSON, nullable=True)
    
    model_provider = Column(String, nullable=True)
    model_name = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    prompt_version = Column(String, nullable=True)
    
    tool_calls_count = Column(Integer, default=0)
    duration_seconds = Column(Integer, nullable=True)
    
    # Store the final structured result JSON
    result_data = Column(JSON, nullable=True)
    
    failure_reason = Column(Text, nullable=True)
    error_info = Column(JSON, nullable=True)
    evidence_references = Column(JSON, nullable=True)
    trace_id = Column(String, nullable=True)
    
    incident = relationship("Incident", back_populates="agent_executions")
