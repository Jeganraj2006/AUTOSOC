"""Stable page and operational read models used by the Phase 5 workspaces."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from autosoc_api.schemas.alert import AlertResponse


class PageMetadata(BaseModel):
    """Server-side pagination metadata.  Totals always describe the filter."""

    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)


class EventSearchResponse(BaseModel):
    events: list[dict[str, Any]]
    page: PageMetadata
    # Retained for existing clients that consumed the pre-pagination contract.
    total: int = Field(ge=0)


class AlertSearchResponse(BaseModel):
    alerts: list[AlertResponse]
    page: PageMetadata


class ResponseApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recommendation_id: UUID
    incident_id: UUID
    requested_at: datetime
    requested_by: str
    reviewer: str | None = None
    decision: str
    decision_at: datetime | None = None
    expiration: datetime | None = None
    reason: str | None = None


class ResponseExecutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recommendation_id: UUID
    approval_id: UUID | None = None
    mode: str
    started_at: datetime
    completed_at: datetime | None = None
    status: str
    executor: str
    verification_status: str | None = None
    rollback_status: str | None = None
    error_category: str | None = None


class GlobalResponseRead(BaseModel):
    """A proposal plus the persisted approval/execution history visible to readers."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    incident_id: UUID
    source: str
    playbook_id: str
    action_type: str
    target_type: str
    target_reference: str
    rationale: str | None = None
    expected_benefit: str | None = None
    evidence_references: list[Any] = Field(default_factory=list)
    impact: str
    reversibility: str
    priority: int
    approval_required: bool
    rollback_available: bool
    status: str
    created_at: datetime
    created_by: str
    approvals: list[ResponseApprovalRead] = Field(default_factory=list)
    executions: list[ResponseExecutionRead] = Field(default_factory=list)


class GlobalResponsePage(BaseModel):
    proposals: list[GlobalResponseRead]
    page: PageMetadata


class AuditRecordRead(BaseModel):
    id: UUID
    timestamp: datetime
    actor_id: str
    actor_name: str | None = None
    action: str
    resource_type: str
    resource_id: str | None = None
    result: str
    correlation_id: str | None = None
    metadata: dict[str, Any] | list[Any] | None = None


class AuditPage(BaseModel):
    records: list[AuditRecordRead]
    page: PageMetadata


OperationalStatus = Literal["healthy", "degraded", "unavailable", "unknown"]


class OperationalComponent(BaseModel):
    name: str
    status: OperationalStatus
    detail: str | None = None
    last_successful_operation: datetime | None = None
    last_heartbeat: datetime | None = None
    failed_processing_count: int | None = Field(default=None, ge=0)
    retry_or_dlq_count: int | None = Field(default=None, ge=0)
    model_identifier: str | None = None


class OperationalHealthResponse(BaseModel):
    components: list[OperationalComponent]
    checked_at: datetime
    limitations: list[str] = Field(default_factory=list)


class IngestionSourceSummary(BaseModel):
    id: UUID
    name: str
    status: str
    last_successful_ingestion: datetime | None = None


class DashboardAggregateResponse(BaseModel):
    time_range: str
    event_count: int | None = Field(default=None, ge=0)
    open_alert_count: int | None = Field(default=None, ge=0)
    critical_incident_count: int | None = Field(default=None, ge=0)
    pending_approval_count: int | None = Field(default=None, ge=0)
    completed_investigation_count: int | None = Field(default=None, ge=0)
    running_investigation_count: int | None = Field(default=None, ge=0)
    failed_investigation_count: int | None = Field(default=None, ge=0)
    ingestion_sources: list[IngestionSourceSummary] = Field(default_factory=list)
    last_successful_data_refresh: datetime | None = None
    partial_failures: list[str] = Field(default_factory=list)
