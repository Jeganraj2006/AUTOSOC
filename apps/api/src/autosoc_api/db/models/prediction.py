import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from autosoc_api.db.base import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), index=True, nullable=False)
    
    generated_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    is_stale = Column(Boolean, default=False)
    
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    attack_version = Column(String(50), nullable=False)
    
    status = Column(String(50), default="completed") # completed, insufficient_evidence, failed
    
    observed_techniques = Column(JSONB, default=list)
    predicted_next_techniques = Column(JSONB, default=list) # List of dicts matching TechniquePrediction
    
    predicted_target = Column(JSONB, nullable=True)
    path_continuation = Column(JSONB, default=list)
    
    escalation_risk_score = Column(Float, default=0.0)
    
    evidence_summary = Column(String, nullable=True)
    limitations = Column(String, default="Forecast based on currently observed evidence; not a confirmed attacker action.")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    incident = relationship("Incident", back_populates="predictions")
