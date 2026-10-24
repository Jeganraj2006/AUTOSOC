from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class IncidentBaseEvent(BaseModel):
    """Base schema for incident lifecycle events published to security.incidents"""
    incident_id: UUID = Field(description="Unique identifier of the incident")
    operation_type: str = Field(description="Type of operation: 'created' or 'updated'")
    
    title: str = Field(description="Incident title")
    status: str = Field(description="Current status (e.g. new, investigating, resolved)")
    severity: str = Field(description="Severity (e.g. low, medium, high, critical)")
    risk_score: float = Field(default=0.0, description="Computed risk score (0-100)")
    
    alert_count: int = Field(description="Total number of correlated alerts")
    primary_entities: List[Dict[str, Any]] = Field(default_factory=list, description="Primary correlated entities")
    
    updated_at: datetime = Field(description="Timestamp of this update")
    trace_id: Optional[str] = Field(None, description="Distributed trace ID")
    schema_version: int = Field(default=1, description="Schema version")

class IncidentCreated(IncidentBaseEvent):
    """Published when a new incident is created"""
    operation_type: str = Field(default="created", description="Type of operation")

class IncidentUpdated(IncidentBaseEvent):
    """Published when an existing incident is updated (e.g. new alerts, status change)"""
    operation_type: str = Field(default="updated", description="Type of operation")
