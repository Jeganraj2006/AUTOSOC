from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID

class IncidentBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=4000)
    severity: str
    status: str
    assignee_id: Optional[str] = Field(None, max_length=255)
    
    risk_score: float = 0.0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    alert_count: int = 0
    event_count: int = 0
    primary_entities: Optional[List[Union[Dict[str, Any], str]]] = []
    tags: Optional[List[str]] = []
    correlation_rule_ids: Optional[List[str]] = []
    candidate_mitre_references: Optional[List[str]] = []
    
    resolution_summary: Optional[str] = None
    closure_reason: Optional[str] = None
    false_positive_reason: Optional[str] = None

class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=4000)
    severity: Optional[str] = None
    status: Optional[str] = None
    assignee_id: Optional[str] = Field(None, max_length=255)
    resolution_summary: Optional[str] = None
    closure_reason: Optional[str] = None
    false_positive_reason: Optional[str] = None

class IncidentResponse(IncidentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class IncidentNoteCreate(BaseModel):
    content: str

class IncidentNoteResponse(BaseModel):
    id: UUID
    incident_id: UUID
    author_id: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

