import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from autosoc_api.db.base import Base

class AttackTactic(Base):
    __tablename__ = "attack_tactics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    short_name = Column(String(100), nullable=True)
    attack_version = Column(String(50), nullable=True)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    techniques = relationship("AttackTechnique", back_populates="tactic")


class AttackTechnique(Base):
    __tablename__ = "attack_techniques"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    
    tactic_id = Column(UUID(as_uuid=True), ForeignKey("attack_tactics.id"), nullable=True)
    
    is_subtechnique = Column(Boolean, default=False)
    parent_technique_id = Column(UUID(as_uuid=True), ForeignKey("attack_techniques.id"), nullable=True)
    
    attack_version = Column(String(50), nullable=True)
    platforms = Column(JSONB, default=list)
    revoked = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tactic = relationship("AttackTactic", back_populates="techniques")
    parent = relationship("AttackTechnique", remote_side=[id], backref="subtechniques")


class AttackRelationship(Base):
    __tablename__ = "attack_relationships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_ref = Column(String(100), index=True, nullable=False)
    target_ref = Column(String(100), index=True, nullable=False)
    relationship_type = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class IncidentAttackMapping(Base):
    __tablename__ = "incident_attack_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), index=True, nullable=False)
    technique_id = Column(UUID(as_uuid=True), ForeignKey("attack_techniques.id"), nullable=False)
    
    status = Column(String(50), default="candidate") # candidate, supported, analyst_confirmed, rejected
    confidence = Column(String(50), nullable=True)
    mapping_source = Column(String(100), nullable=True) # detection_rule, analyst, ml_context
    
    evidence_summary = Column(String, nullable=True)
    source_alert_ids = Column(JSONB, default=list)
    source_event_ids = Column(JSONB, default=list)
    
    mapped_at = Column(DateTime, default=datetime.utcnow)
    mapped_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    rejection_reason = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    incident = relationship("Incident", back_populates="attack_mappings")
    technique = relationship("AttackTechnique")
