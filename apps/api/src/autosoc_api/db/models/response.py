import uuid
from datetime import datetime, UTC
from typing import Optional, List

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from autosoc_api.db.base import Base

class ResponseRecommendation(Base):
    """
    Represents a suggested containment/response action (either from an analyst, policy, or AI).
    """
    __tablename__ = "response_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    
    source = Column(String, nullable=False) # 'analyst', 'agent', 'policy'
    playbook_id = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    
    target_type = Column(String, nullable=False) # e.g., 'ip', 'user', 'host'
    target_reference = Column(String, nullable=False) # e.g., '192.168.1.100'
    
    rationale = Column(Text, nullable=True)
    expected_benefit = Column(Text, nullable=True)
    evidence_references = Column(JSON, default=list) # List of alert IDs or similar
    
    impact = Column(String, nullable=False) # 'low', 'medium', 'high', 'critical'
    reversibility = Column(String, nullable=False) # 'reversible', 'partially_reversible', 'non_reversible'
    priority = Column(Integer, default=3)
    
    approval_required = Column(Boolean, default=True)
    rollback_available = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    created_by = Column(String, nullable=False) # Analyst ID or 'system'
    
    status = Column(String, default="proposed", nullable=False)
    # proposed, pending_review, approved, rejected, expired, executed, failed, rolled_back, cancelled
    
    # Relationships
    approvals = relationship("ResponseApproval", back_populates="recommendation", cascade="all, delete-orphan")
    executions = relationship("ResponseExecution", back_populates="recommendation", cascade="all, delete-orphan")


class ResponseApproval(Base):
    """
    Tracks the human approval request and decision for a response recommendation.
    """
    __tablename__ = "response_approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("response_recommendations.id", ondelete="CASCADE"), nullable=False)
    incident_id = Column(UUID(as_uuid=True), nullable=False) # Denormalized for convenience
    
    requested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    requested_by = Column(String, nullable=False)
    
    reviewer = Column(String, nullable=True) # Identity of the approver/rejecter
    decision = Column(String, default="pending", nullable=False) # pending, approved, rejected, expired, cancelled
    decision_at = Column(DateTime(timezone=True), nullable=True)
    reason = Column(Text, nullable=True) # E.g., why it was rejected
    
    expiration = Column(DateTime(timezone=True), nullable=True)
    
    recommendation = relationship("ResponseRecommendation", back_populates="approvals")


class ResponseExecution(Base):
    """
    Tracks an actual instance of executing an approved response action.
    """
    __tablename__ = "response_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("response_recommendations.id", ondelete="CASCADE"), nullable=False)
    approval_id = Column(UUID(as_uuid=True), ForeignKey("response_approvals.id", ondelete="SET NULL"), nullable=True)
    
    playbook_id = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    mode = Column(String, nullable=False) # dry_run, simulation, analyst_approved_execution
    
    target = Column(String, nullable=False)
    
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(String, default="queued", nullable=False)
    # queued, validating, running, verifying, succeeded, failed, timed_out, rollback_pending, rolling_back, rolled_back, cancelled, blocked
    
    executor = Column(String, nullable=False) # The specific executor class/name used
    result = Column(JSON, nullable=True)
    
    verification_status = Column(String, nullable=True) # pending, verified, failed
    rollback_status = Column(String, nullable=True) # pending, rolled_back, failed
    
    error_category = Column(String, nullable=True)
    idempotency_key = Column(String, nullable=False, unique=True)
    
    recommendation = relationship("ResponseRecommendation", back_populates="executions")
