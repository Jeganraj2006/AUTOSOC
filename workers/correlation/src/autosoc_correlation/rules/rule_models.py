from pydantic import BaseModel
from typing import List, Optional

class CorrelationRule(BaseModel):
    id: str
    name: str
    description: str
    severity: str
    time_window_seconds: int
    required_entities: List[str]  # e.g., ["source_ip", "user"]
    trigger_threshold: int
    mitre_tactics: Optional[List[str]] = []
