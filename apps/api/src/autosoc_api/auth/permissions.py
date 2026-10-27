from typing import List, Dict

class Permissions:
    USERS_READ = "users:read"
    USERS_MANAGE = "users:manage"
    DATASOURCES_READ = "datasources:read"
    DATASOURCES_MANAGE = "datasources:manage"
    RULES_READ = "rules:read"
    RULES_MANAGE = "rules:manage"
    ALERTS_READ = "alerts:read"
    ALERTS_UPDATE = "alerts:update"
    INCIDENTS_READ = "incidents:read"
    INCIDENTS_UPDATE = "incidents:update"
    EVENTS_READ = "events:read"
    EVENTS_INGEST = "events:ingest"
    EVENTS_DETECT = "events:detect"
    PREDICTIONS_READ = "predictions:read"
    PREDICTIONS_MANAGE = "predictions:manage"
    AGENTS_READ = "agents:read"
    AGENTS_RUN = "agents:run"
    RESPONSES_READ = "responses:read"
    RESPONSES_APPROVE = "responses:approve"
    RESPONSES_RECOMMEND = "responses:recommend"
    RESPONSES_EXECUTE = "responses:execute"
    RESPONSES_MANAGE = "responses:manage"
    REPORTS_READ = "reports:read"
    REPORTS_EXPORT = "reports:export"
    AUDIT_READ = "audit:read"
    SETTINGS_READ = "settings:read"
    SETTINGS_MANAGE = "settings:manage"

ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "administrator": [
        Permissions.USERS_READ, Permissions.USERS_MANAGE,
        Permissions.DATASOURCES_READ, Permissions.DATASOURCES_MANAGE,
        Permissions.RULES_READ, Permissions.RULES_MANAGE,
        Permissions.ALERTS_READ, Permissions.ALERTS_UPDATE,
        Permissions.INCIDENTS_READ, Permissions.INCIDENTS_UPDATE,
        Permissions.EVENTS_READ, Permissions.EVENTS_INGEST, Permissions.EVENTS_DETECT,
        Permissions.PREDICTIONS_READ, Permissions.PREDICTIONS_MANAGE,
        Permissions.AGENTS_READ, Permissions.AGENTS_RUN,
        Permissions.RESPONSES_READ, Permissions.RESPONSES_APPROVE,
        Permissions.RESPONSES_RECOMMEND, Permissions.RESPONSES_EXECUTE,
        Permissions.SETTINGS_READ, Permissions.SETTINGS_MANAGE,
        Permissions.AUDIT_READ, Permissions.RESPONSES_MANAGE,
    ],
    "soc_analyst": [
        Permissions.ALERTS_READ, Permissions.ALERTS_UPDATE,
        Permissions.INCIDENTS_READ, Permissions.INCIDENTS_UPDATE,
        Permissions.EVENTS_READ, Permissions.EVENTS_DETECT,
        Permissions.PREDICTIONS_READ, Permissions.PREDICTIONS_MANAGE,
        Permissions.AGENTS_READ, Permissions.AGENTS_RUN, Permissions.RESPONSES_READ,
        Permissions.RESPONSES_RECOMMEND, Permissions.RESPONSES_EXECUTE,
        Permissions.DATASOURCES_READ, Permissions.RULES_READ, Permissions.SETTINGS_READ
    ],
    "security_manager": [
        Permissions.ALERTS_READ, Permissions.INCIDENTS_READ, Permissions.EVENTS_READ, Permissions.REPORTS_READ,
        Permissions.REPORTS_EXPORT, Permissions.DATASOURCES_READ, Permissions.RULES_READ,
        Permissions.SETTINGS_READ, Permissions.RESPONSES_READ, Permissions.RESPONSES_APPROVE,
        Permissions.RESPONSES_EXECUTE
    ],
    "auditor": [
        Permissions.AUDIT_READ, Permissions.INCIDENTS_READ, Permissions.EVENTS_READ,
        Permissions.REPORTS_READ, Permissions.ALERTS_READ, Permissions.PREDICTIONS_READ,
        Permissions.AGENTS_READ, Permissions.RESPONSES_READ, Permissions.DATASOURCES_READ,
        Permissions.RULES_READ, Permissions.SETTINGS_READ,
    ],
    # Keycloak provisions the development read-only account with ``viewer``.
    # Keep it explicitly read-only while allowing it to inspect the SOC data
    # and response history needed to understand an incident.
    "viewer": [
        Permissions.ALERTS_READ, Permissions.INCIDENTS_READ, Permissions.EVENTS_READ,
        Permissions.PREDICTIONS_READ, Permissions.AGENTS_READ, Permissions.RESPONSES_READ,
        Permissions.REPORTS_READ, Permissions.AUDIT_READ, Permissions.DATASOURCES_READ,
        Permissions.RULES_READ, Permissions.SETTINGS_READ,
    ],
}

def get_permissions_for_roles(roles: List[str]) -> List[str]:
    perms = set()
    for role in roles:
        perms.update(ROLE_PERMISSIONS.get(role, []))
    return list(perms)
