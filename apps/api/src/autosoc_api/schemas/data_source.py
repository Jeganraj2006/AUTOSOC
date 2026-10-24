from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class DataSourceBase(BaseModel):
    name: str = Field(..., max_length=255)
    source_type: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    enabled: bool = True
    environment: str = Field(default="production", max_length=50)

class DataSourceCreate(DataSourceBase):
    secret_reference: Optional[str] = Field(None, max_length=255)

class DataSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    enabled: Optional[bool] = None
    environment: Optional[str] = Field(None, max_length=50)
    secret_reference: Optional[str] = Field(None, max_length=255)

class DataSourceResponse(DataSourceBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DataSourceListResponse(BaseModel):
    items: list[DataSourceResponse]
    total: int
