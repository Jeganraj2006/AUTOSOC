from pydantic import BaseModel, ConfigDict, Field, UUID4
from typing import List, Optional, Any, Dict
from datetime import datetime

class ResponseRecommendationBase(BaseModel):
    incident_id: UUID4
    source: str
    playbook_id: str
    action_type: str
    target_type: str
    target_reference: str
    rationale: Optional[str] = None
    expected_benefit: Optional[str] = None
    evidence_references: List[Any] = Field(default_factory=list)
    impact: str
    reversibility: str
    priority: int = 3
    approval_required: bool = True
    rollback_available: bool = True

class ResponseRecommendationCreate(ResponseRecommendationBase):
    pass

class ResponseRecommendationResponse(ResponseRecommendationBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID4
    status: str
    created_at: datetime
    created_by: str

class ResponseApprovalBase(BaseModel):
    recommendation_id: UUID4
    incident_id: UUID4
    reason: Optional[str] = None

class ResponseApprovalRequest(ResponseApprovalBase):
    pass

class ResponseApprovalAction(BaseModel):
    decision: str # "approved" or "rejected"
    reason: Optional[str] = None

class ResponseApprovalResponse(ResponseApprovalBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID4
    requested_at: datetime
    requested_by: str
    reviewer: Optional[str] = None
    decision: str
    decision_at: Optional[datetime] = None
    expiration: Optional[datetime] = None

class ResponseExecutionBase(BaseModel):
    recommendation_id: UUID4
    mode: str # dry_run, simulation, analyst_approved_execution

class ResponseExecutionCreate(ResponseExecutionBase):
    pass

class ResponseExecutionResponse(ResponseExecutionBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID4
    approval_id: Optional[UUID4] = None
    playbook_id: str
    action_type: str
    target: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    executor: str
    result: Optional[Dict[str, Any]] = None
    verification_status: Optional[str] = None
    rollback_status: Optional[str] = None
    error_category: Optional[str] = None
    idempotency_key: str
