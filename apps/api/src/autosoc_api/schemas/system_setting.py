from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class SystemSettingBase(BaseModel):
    key: str = Field(..., max_length=100)
    value: str = Field(..., max_length=2000)
    description: Optional[str] = Field(None, max_length=1000)

class SystemSettingCreate(SystemSettingBase):
    pass

class SystemSettingUpdate(BaseModel):
    value: Optional[str] = Field(None, max_length=2000)
    description: Optional[str] = Field(None, max_length=1000)

class SystemSettingResponse(SystemSettingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
