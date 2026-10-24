from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
import uuid
from enum import Enum

class AgentExecutionStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    BLOCKED_BY_POLICY = "blocked_by_policy"

class AgentExecutionBase(BaseModel):
    incident_id: uuid.UUID
    workflow_type: str = "full_investigation"
    
class AgentExecutionCreate(AgentExecutionBase):
    requested_by: Optional[str] = None
    
class AgentResultSection(BaseModel):
    findings: List[str] = []
    confidence: str = "low"
    evidence_references: List[str] = []
    retrieved_source_references: List[str] = []
    assumptions: List[str] = []
    uncertainties: List[str] = []
    recommendations: List[str] = []

class AgentResult(BaseModel):
    agent_name: str
    execution_id: uuid.UUID
    incident_id: uuid.UUID
    status: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    model_name: str
    prompt_version: str
    schema_version: str = "1.0"
    
    detection_verification: Optional[AgentResultSection] = None
    investigation: Optional[AgentResultSection] = None
    threat_intelligence: Optional[AgentResultSection] = None
    risk_assessment: Optional[AgentResultSection] = None
    prediction_analysis: Optional[AgentResultSection] = None
    response_recommendation: Optional[AgentResultSection] = None
    reporting: Optional[Dict[str, Any]] = None

class AgentExecutionResponse(AgentExecutionBase):
    id: uuid.UUID
    status: AgentExecutionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    requested_by: Optional[str] = None
    current_step: Optional[str] = None
    steps_completed: int
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    prompt_version: Optional[str] = None
    tool_calls_count: int
    duration_seconds: Optional[int] = None
    result_data: Optional[Dict[str, Any]] = None
    failure_reason: Optional[str] = None
    trace_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
