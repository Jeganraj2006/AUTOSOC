from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

class EntityRef(BaseModel):
    """Reference to an extracted entity within the alert."""
    type: str = Field(description="Entity type e.g., user, host, ip, file, process")
    value: str = Field(description="The canonical value of the entity")

class DetectionResult(BaseModel):
    """
    Schema for a generated detection alert.
    Represents the output of the rule engine before persistence or aggregation.
    """
    detection_id: UUID = Field(description="Unique identifier for this specific detection match")
    alert_id: Optional[UUID] = Field(
        default=None,
        description="Database alert identifier assigned after durable persistence.",
    )
    rule_id: str = Field(description="Identifier of the rule that triggered")
    rule_version: str = Field(description="Version of the rule that matched")
    rule_name: str = Field(description="Human-readable rule name")
    rule_type: str = Field(description="Type of rule (e.g., threshold, exact, sigma)")
    
    event_ids: List[UUID] = Field(description="List of normalized_event_ids that contributed to this detection")
    source_ids: List[str] = Field(description="List of ingestion source identities")
    
    detected_at: datetime = Field(description="UTC timestamp when the detection occurred")
    
    severity: str = Field(description="Severity: informational, low, medium, high, critical")
    confidence: float = Field(description="Deterministic confidence score from 0.0 to 1.0")
    
    title: str = Field(description="Generated alert title")
    description: str = Field(description="Human-readable explanation of why this rule triggered")
    
    evidence: List[Dict[str, Any]] = Field(description="Subset of event data serving as direct evidence")
    entities: List[EntityRef] = Field(default_factory=list, description="Extracted relevant entities")
    
    candidate_mitre_techniques: List[str] = Field(default_factory=list, description="Candidate MITRE ATT&CK technique IDs")
    recommended_investigation: Optional[str] = Field(None, description="Recommended steps for the SOC analyst")
    
    trace_id: Optional[str] = Field(None, description="Distributed trace ID for troubleshooting")
    schema_version: int = Field(default=1, description="Schema version of this detection result")

    # ML Specific Extensions (Phase 11)
    detection_source: str = Field(default="rule", description="Source of detection: 'rule' or 'ml'")
    detection_type: Optional[str] = Field(default=None, description="Detailed type: 'known_attack', 'suspicious_anomaly', 'potential_zero_day_behavior'")
    predicted_known_family: Optional[str] = Field(None, description="Predicted malware/attack family if known")
    supervised_confidence: Optional[float] = Field(None, description="Calibrated confidence from supervised ensemble")
    anomaly_score: Optional[float] = Field(None, description="Normalized anomaly score")
    hybrid_risk_score: Optional[float] = Field(None, description="Computed hybrid risk score")
    model_votes: Optional[Dict[str, str]] = Field(None, description="Individual model decisions/votes")
    model_versions: Optional[Dict[str, str]] = Field(None, description="Versions of the ML models used")
    feature_version: Optional[str] = Field(None, description="Version of the feature contract used")
    reasons: Optional[List[str]] = Field(default_factory=list, description="List of reasons for the decision")
