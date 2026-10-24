from pydantic import BaseModel
from typing import Dict, Any

class HealthResponse(BaseModel):
    status: str
    components: Dict[str, str] = {}
    dependencies: Dict[str, str] = {}

class VersionResponse(BaseModel):
    app_name: str
    app_version: str
    api_version: str
    environment: str
    commit_id: str
