from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

class NormalizedSecurityEvent(BaseModel):
    """
    Canonical security event schema (OCSF-inspired) representing a normalized security event.
    """
    # Identity
    event_id: UUID = Field(description="Unique identifier for the raw event")
    normalized_event_id: UUID = Field(description="Unique identifier for this normalized event")
    ingestion_id: UUID = Field(description="Identifier for the ingestion batch")
    source_id: str = Field(description="DataSource identity")
    source_type: str = Field(description="Type of the source (e.g., syslog, cloudtrail)")
    schema_version: int = Field(default=1, description="Version of the normalized schema")

    # Time
    event_time: Optional[datetime] = Field(None, description="Best-effort exact time the event occurred in UTC")
    received_at: datetime = Field(description="UTC timestamp when the event was received by the collector")
    normalized_at: datetime = Field(description="UTC timestamp when normalization occurred")
    timezone_original: Optional[str] = Field(None, description="Original timezone string if provided")
    timestamp_quality: str = Field(
        default="exact", 
        description="Indicator of timestamp precision (e.g., 'exact', 'inferred_timezone', 'received_time_fallback', 'invalid')"
    )

    # Event classification
    event_category: str = Field(description="High-level category (e.g., authentication, network, process)")
    event_type: str = Field(description="Sub-category (e.g., login, connection)")
    event_action: Optional[str] = Field(None, description="Specific action performed")
    event_outcome: str = Field(default="unknown", description="Outcome (success, failure, unknown, allowed, denied)")
    severity_source: Optional[str] = Field(None, description="Severity string from the original source")
    message: Optional[str] = Field(None, description="Human-readable message or summary")

    # Network
    source_ip: Optional[str] = Field(None, description="Source IP address")
    source_port: Optional[int] = Field(None, description="Source port number")
    destination_ip: Optional[str] = Field(None, description="Destination IP address")
    destination_port: Optional[int] = Field(None, description="Destination port number")
    protocol: Optional[str] = Field(None, description="Network protocol (e.g., TCP, UDP)")
    transport: Optional[str] = Field(None, description="Transport layer")
    direction: Optional[str] = Field(None, description="Flow direction (inbound, outbound)")
    bytes_in: Optional[int] = Field(None, description="Bytes received")
    bytes_out: Optional[int] = Field(None, description="Bytes sent")
    packets_in: Optional[int] = Field(None, description="Packets received")
    packets_out: Optional[int] = Field(None, description="Packets sent")
    session_duration: Optional[int] = Field(None, description="Duration in milliseconds")

    # Identity
    username: Optional[str] = Field(None, description="Username associated with the event")
    user_id: Optional[str] = Field(None, description="Unique user identifier")
    user_domain: Optional[str] = Field(None, description="Domain of the user")
    user_type: Optional[str] = Field(None, description="Type of user (e.g., system, regular)")
    privilege_level: Optional[str] = Field(None, description="Privilege level context")

    # Host
    hostname: Optional[str] = Field(None, description="Hostname involved in the event")
    host_id: Optional[str] = Field(None, description="Unique host identifier")
    host_ip: Optional[str] = Field(None, description="IP address of the host")
    operating_system: Optional[str] = Field(None, description="Operating system name")

    # Process
    process_name: Optional[str] = Field(None, description="Name of the process")
    process_id: Optional[int] = Field(None, description="Process identifier (PID)")
    process_path: Optional[str] = Field(None, description="File path of the process executable")
    command_line: Optional[str] = Field(None, description="Execution command line")
    parent_process_name: Optional[str] = Field(None, description="Name of the parent process")
    parent_process_id: Optional[int] = Field(None, description="Parent Process identifier (PPID)")

    # File
    file_name: Optional[str] = Field(None, description="Name of the file involved")
    file_path: Optional[str] = Field(None, description="Path to the file")
    file_hashes: Dict[str, str] = Field(default_factory=dict, description="Dictionary of hash types and values")

    # Authentication
    authentication_method: Optional[str] = Field(None, description="Method used for authentication")
    authentication_result: Optional[str] = Field(None, description="Result of authentication attempt")
    failure_reason: Optional[str] = Field(None, description="Reason if authentication failed")

    # Cloud
    cloud_provider: Optional[str] = Field(None, description="Cloud service provider")
    cloud_account_id: Optional[str] = Field(None, description="Cloud account ID")
    cloud_region: Optional[str] = Field(None, description="Cloud region")
    resource_type: Optional[str] = Field(None, description="Type of cloud resource")
    resource_id: Optional[str] = Field(None, description="Identifier of the cloud resource")
    api_operation: Optional[str] = Field(None, description="Cloud API operation name")

    # Kubernetes
    cluster_name: Optional[str] = Field(None, description="Kubernetes cluster name")
    namespace: Optional[str] = Field(None, description="Kubernetes namespace")
    pod_name: Optional[str] = Field(None, description="Kubernetes pod name")
    container_name: Optional[str] = Field(None, description="Kubernetes container name")
    service_account: Optional[str] = Field(None, description="Kubernetes service account")

    # Provenance
    raw_event_reference: str = Field(description="Reference or locator to retrieve the raw event (e.g. MinIO key)")
    raw_payload_hash: str = Field(description="Hash of the raw payload to guarantee integrity")
    parser_name: str = Field(description="Name of the parser used to generate this normalized event")
    parser_version: str = Field(description="Version of the parser")
    normalization_confidence: str = Field(default="high", description="Confidence in the extraction (high, medium, low)")
    normalization_warnings: List[str] = Field(default_factory=list, description="Warnings encountered during normalization")
    trace_id: Optional[str] = Field(None, description="Distributed trace ID")
    request_id: Optional[str] = Field(None, description="Original request ID from ingestion")

class EnrichedSecurityEvent(NormalizedSecurityEvent):
    """
    Normalized event enriched with additional business and threat context.
    """
    schema_version: int = Field(default=1, description="Version of the enriched schema")

    # Asset Context
    asset_criticality: Optional[str] = Field(None, description="Criticality of the associated asset")
    asset_category: Optional[str] = Field(None, description="Category of the asset")
    asset_environment: Optional[str] = Field(None, description="Environment the asset belongs to")
    asset_business_role: Optional[str] = Field(None, description="Business role of the asset")
    asset_owner_reference: Optional[str] = Field(None, description="Reference to the asset owner")

    # User Context
    user_privilege_category: Optional[str] = Field(None, description="Privilege category of the user")
    user_department: Optional[str] = Field(None, description="Department of the user")
    is_service_account: Optional[bool] = Field(None, description="Whether the user is a service account")

    # Network Context
    geo_country: Optional[str] = Field(None, description="Country of the remote IP")
    geo_region: Optional[str] = Field(None, description="Region of the remote IP")
    geo_city: Optional[str] = Field(None, description="City of the remote IP")
    asn: Optional[str] = Field(None, description="Autonomous System Number")
    ip_classification: Optional[str] = Field(None, description="Classification of the IP (e.g. public, private)")
    ip_reputation_status: Optional[str] = Field(None, description="Reputation status of the IP")

    # Vulnerability Context
    vuln_count: Optional[int] = Field(None, description="Number of known vulnerabilities on the asset")
    vuln_highest_severity: Optional[str] = Field(None, description="Highest severity vulnerability present")
    vuln_cve_references: List[str] = Field(default_factory=list, description="Relevant CVE references")

    # Historical Context
    entity_first_seen: Optional[datetime] = Field(None, description="First time this entity was observed")
    entity_last_seen: Optional[datetime] = Field(None, description="Most recent time this entity was observed prior")
    event_frequency: Optional[str] = Field(None, description="Frequency categorization of this event type")
    is_rare_entity: Optional[bool] = Field(None, description="Indicator if the entity is rarely seen")

    # Threat Intelligence Context
    ti_indicator_match_refs: List[str] = Field(default_factory=list, description="References to matching TI indicators")
    ti_source_refs: List[str] = Field(default_factory=list, description="Sources of the TI data")
    ti_confidence: Optional[str] = Field(None, description="Confidence of the TI match")
    ti_expiration: Optional[datetime] = Field(None, description="Expiration time of the TI indicator")

    # MITRE Candidate Context
    candidate_mitre_techniques: List[str] = Field(default_factory=list, description="Candidate technique IDs")
    candidate_mitre_confidence: Optional[str] = Field(None, description="Confidence in the candidate mapping")
    candidate_mitre_source: Optional[str] = Field(None, description="Source of the candidate mapping")
