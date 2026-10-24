from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class AuditLogResponse(BaseModel):
    id: UUID
    actor_id: str
    actor_name: Optional[str] = None
    actor_roles: Optional[str] = None
    action: str
    target_type: str
    target_id: Optional[str] = None
    status: str
    request_id: Optional[str] = None
    source_ip: Optional[str] = None
    reason: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
