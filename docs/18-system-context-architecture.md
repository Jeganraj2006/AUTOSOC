# System Context Architecture

## C4 System Context Diagram

```mermaid
C4Context
    title System Context for AutoSOC Platform

    Person(admin, "Administrator", "Manages system configuration, data sources, and rules.")
    Person(analyst, "SOC Analyst", "Investigates incidents and approves responses.")
    Person(manager, "Security Manager", "Reviews reports and risk metrics.")
    Person(auditor, "Auditor", "Reviews audit logs and compliance.")

    System_Ext(security_sources, "Security Data Sources", "Syslog, Windows, CloudTrail, NetFlow, k8s audit.")
    System_Ext(keycloak, "Keycloak (IAM)", "Provides OIDC authentication and identity management.")
    System_Ext(threat_intel, "Threat Intelligence Sources", "External APIs providing IoCs and context.")
    System_Ext(llm_provider, "Local LLM Runtime", "Ollama instance serving foundational models.")
    System_Ext(response_targets, "Approved Response Targets", "Firewalls, IAM systems, Mock APIs (for dry-runs).")
    System_Ext(ci_cd, "CI/CD Environment", "GitHub Actions building and testing the system.")

    System(autosoc, "AutoSOC Platform", "Autonomous Security Operations Center for zero-day detection and agentic investigation.")

    Rel(admin, autosoc, "Configures and manages", "HTTPS")
    Rel(analyst, autosoc, "Investigates and approves", "HTTPS")
    Rel(manager, autosoc, "Views reports", "HTTPS")
    Rel(auditor, autosoc, "Audits actions", "HTTPS")

    Rel(security_sources, autosoc, "Sends raw security events", "TCP/UDP/HTTPS")
    Rel(autosoc, keycloak, "Authenticates users via OIDC", "HTTPS")
    Rel(autosoc, threat_intel, "Fetches enrichment data", "HTTPS")
    Rel(autosoc, llm_provider, "Sends prompts, receives generation", "HTTP/REST")
    Rel(autosoc, response_targets, "Executes approved actions", "HTTPS/API")
    
    Rel(ci_cd, autosoc, "Builds, scans, and deploys containers", "Git/Docker")
```

## External Entities Description

### Keycloak (IAM)
- **Purpose**: Centralized authentication and RBAC.
- **Data Exchanged**: Login credentials (handled by Keycloak UI), OIDC tokens.
- **Authentication Method**: Standard OIDC protocols.
- **Trust Level**: High (Trusted core infrastructure component).
- **Security Considerations**: Must be secured via HTTPS; token lifetimes must be kept short.

### Security Data Sources
- **Purpose**: Systems generating the raw logs the SOC monitors.
- **Data Exchanged**: Unstructured or semi-structured raw log data.
- **Authentication Method**: API keys or mutual TLS depending on the source.
- **Trust Level**: Low (Input must be treated as potentially malicious or malformed).
- **Security Considerations**: Susceptible to log injection attacks; requires strict validation.

### Threat Intelligence Sources
- **Purpose**: Enriches logs with context (e.g., known malicious IPs).
- **Data Exchanged**: IP addresses, file hashes, reputation scores.
- **Authentication Method**: API Keys.
- **Trust Level**: Medium.
- **Security Considerations**: External APIs might rate-limit or fail, requiring safe fallback.

### Local LLM Runtime (Ollama)
- **Purpose**: Provides AI generation capabilities without exposing data to the cloud.
- **Data Exchanged**: Prompts (containing masked event context), generated text.
- **Authentication Method**: Local network isolation / simple API key.
- **Trust Level**: Medium (Model output is untrusted and must be validated).
- **Security Considerations**: Vulnerable to prompt injection from raw logs.

### Approved Response Targets
- **Purpose**: External systems where containment actions are executed.
- **Data Exchanged**: API commands (e.g., `block_ip`, `disable_user`).
- **Authentication Method**: Dedicated service accounts / API keys.
- **Trust Level**: High.
- **Security Considerations**: Credentials for these systems must be stored securely (e.g., Vault or Kubernetes Secrets) and never exposed to the frontend or directly to the LLM.

### CI/CD Environment (GitHub Actions)
- **Purpose**: Automates testing, security scanning, and container building.
- **Data Exchanged**: Source code, test results, container images.
- **Authentication Method**: GitHub access tokens.
- **Trust Level**: High.
- **Security Considerations**: Must prevent malicious PRs from exfiltrating secrets.
