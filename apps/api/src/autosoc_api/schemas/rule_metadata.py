from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class RuleMetadataBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    rule_type: str = Field(..., max_length=50)
    enabled: bool = False
    severity: str = Field(..., max_length=20)
    version: int = 1
    mitre_references_json: Optional[str] = Field(None, max_length=1000)
    file_path: Optional[str] = Field(None, max_length=500)

class RuleMetadataCreate(RuleMetadataBase):
    pass

class RuleMetadataUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    enabled: Optional[bool] = None
    severity: Optional[str] = Field(None, max_length=20)
    version: Optional[int] = None
    mitre_references_json: Optional[str] = Field(None, max_length=1000)
    file_path: Optional[str] = Field(None, max_length=500)

class RuleMetadataResponse(RuleMetadataBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
