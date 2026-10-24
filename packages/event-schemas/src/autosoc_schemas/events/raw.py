from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID

class RawSecurityEvent(BaseModel):
    """
    Standard ingestion envelope for all raw security events.
    """
    event_id: UUID = Field(description="Unique identifier for the event")
    ingestion_id: UUID = Field(description="Unique identifier for the ingestion request/batch")
    source_id: str = Field(description="DataSource identity")
    source_type: str = Field(description="The type of the source (e.g., syslog, http_json)")
    source_name: str = Field(description="Human readable name of the source")
    received_at: datetime = Field(description="UTC timestamp when the event was received by the collector")
    source_timestamp: Optional[datetime] = Field(None, description="UTC timestamp extracted from the raw event if available safely")
    content_type: str = Field(description="MIME type of the payload (e.g., application/json, text/plain)")
    schema_version: int = Field(default=1, description="Version of the raw event schema")
    payload: str = Field(description="The unmodified raw event payload (JSON string or text)")
    payload_hash: str = Field(description="SHA-256 hash of the payload for deduplication and integrity")
    ingestion_method: str = Field(description="Method used to ingest the event (e.g., generic_http, syslog_udp)")
    collector_version: str = Field(description="Version of the ingestion worker/collector")
    trace_id: Optional[str] = Field(None, description="Distributed trace ID for observability")
    request_id: Optional[str] = Field(None, description="HTTP request ID or equivalent")
    tenant_or_environment: str = Field(default="production", description="Tenant or environment segregation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Safe transport-level metadata. No raw credentials allowed.")

class FailedSecurityEvent(BaseModel):
    """
    Schema for events that failed to process or parse after initial receipt.
    """
    failure_id: UUID
    ingestion_id: Optional[UUID] = None
    source_id: Optional[str] = None
    source_type: Optional[str] = None
    received_at: datetime
    failure_stage: str = Field(description="The pipeline stage where the failure occurred")
    failure_reason_code: str = Field(description="Machine-readable failure code")
    failure_description: str = Field(description="Human-readable safe failure reason")
    payload_hash: Optional[str] = None
    trace_id: Optional[str] = None
    retryable: bool = False
    retry_count: int = 0
    schema_version: int = 1
    safe_metadata: Dict[str, Any] = Field(default_factory=dict)
    # The actual payload is NOT included by default to prevent DLQ bloat/poisoning,
    # unless specifically needed, but a reference to the archive should be in safe_metadata.

class IngestionStatus(BaseModel):
    event_id: Optional[UUID] = None
    status: str
    error: Optional[str] = None
    duplicate: bool = False

class SourceHealth(BaseModel):
    source_id: str
    status: str # healthy, degraded, error
    last_received_at: Optional[datetime] = None
    last_successful_ingestion: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0

class IngestionResult(BaseModel):
    ingestion_id: UUID
    received: int
    accepted: int
    rejected: int
    duplicates: int
    events: list[IngestionStatus]
