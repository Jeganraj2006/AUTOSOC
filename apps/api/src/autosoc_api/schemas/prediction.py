import uuid
from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class PredictionTarget(BaseModel):
    target_type: str = Field(description="e.g. user, host, IP, process")
    target_entity: Optional[str] = Field(None, description="Exact entity identifier if highly confident")

class TechniquePrediction(BaseModel):
    technique_id: str
    probability: Optional[float] = None
    score: Optional[float] = None
    predicted_tactic: Optional[str] = None
    defensive_recommendation: Optional[str] = None

class PredictionResult(BaseModel):
    prediction_id: uuid.UUID
    incident_id: uuid.UUID
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    
    observed_techniques: List[str] = Field(default_factory=list)
    predicted_next_techniques: List[TechniquePrediction] = Field(default_factory=list)
    
    predicted_target: Optional[PredictionTarget] = None
    path_continuation: List[str] = Field(default_factory=list, description="Up to 3-step probable continuation")
    
    escalation_risk_score: float = Field(0.0, description="Risk that next step represents escalation")
    
    model_name: str
    model_version: str
    attack_version: str
    
    confidence: str = Field(default="low")
    evidence: str = Field(default="")
    limitations: str = Field(default="Forecast based on currently observed evidence; not a confirmed attacker action.")
    
    trace_id: Optional[str] = None
    schema_version: str = "1.0"
