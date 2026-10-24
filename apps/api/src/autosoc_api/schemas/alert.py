from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class AlertBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    severity: str
    status: str
    source_event_id: Optional[str] = Field(None, max_length=255)
    rule_id: Optional[str] = None
    indicators_json: Optional[Any] = None
    incident_id: Optional[UUID] = None

class AlertUpdate(BaseModel):
    status: Optional[str] = None
    incident_id: Optional[UUID] = None

class AlertResponse(AlertBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
