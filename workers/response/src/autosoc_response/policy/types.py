from enum import Enum

class ActionType(str, Enum):
    INCREASE_MONITORING = "increase_monitoring"
    BLOCK_IP = "block_ip"
    DISABLE_ACCOUNT = "disable_account"
    ISOLATE_HOST = "isolate_host"
    TERMINATE_SESSION = "terminate_session"
    REVOKE_CLOUD_SESSION = "revoke_cloud_session"
    ROTATE_CREDENTIAL = "rotate_credential"
    QUARANTINE_FILE = "quarantine_file"
    RESTRICT_CLOUD_RESOURCE = "restrict_cloud_resource"
    KUBERNETES_ISOLATE_WORKLOAD = "kubernetes_isolate_workload"
    COLLECT_ADDITIONAL_EVIDENCE = "collect_additional_evidence"

class ImpactLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ReversibilityType(str, Enum):
    REVERSIBLE = "reversible"
    PARTIALLY_REVERSIBLE = "partially_reversible"
    NON_REVERSIBLE = "non_reversible"

class ExecutionMode(str, Enum):
    RECOMMENDATION = "recommendation"
    DRY_RUN = "dry_run"
    SIMULATION = "simulation"
    ANALYST_APPROVED_EXECUTION = "analyst_approved_execution"

class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    LAB = "lab"
    SANDBOX = "sandbox"
    PRODUCTION = "production"
