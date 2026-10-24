# STRIDE Threat Model

This document outlines the STRIDE threat analysis for core AutoSOC components.

*Note: S=Spoofing, T=Tampering, R=Repudiation, I=Information Disclosure, D=Denial of Service, E=Elevation of Privilege.*

| ID | Component | STRIDE | Description | Precondition | Impact | Risk | Preventive | Detective | Recovery |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| TM-01 | Browser/Frontend | S, I | Attacker steals session token via XSS. | UI fails to sanitize AI output. | High | High | React/Next.js auto-escaping; CSP headers. | Unusual login IP alerts. | Revoke token in Keycloak. |
| TM-02 | FastAPI Backend | T, E | Attacker bypasses RBAC to approve response. | API lacks route-level role checks. | Critical | High | Strict FastAPI Depends(RoleChecker). | Audit log analysis. | Revert action via playbook. |
| TM-03 | Auth Flow (Keycloak) | S, I | Attacker brute-forces analyst password. | Weak password policy. | High | Med | Account lockout; enforced MFA. | Failed login alerts. | Reset password. |
| TM-04 | Event Collectors | S, D | Attacker floods API with fake syslogs. | Publicly exposed API without auth. | Low | High | API keys; rate-limiting in Redis. | 429 status spikes. | IP banning at WAF. |
| TM-05 | Redpanda | T, D | Attacker deletes topics or floods partitions. | Unauthenticated access to broker. | High | High | TLS & SASL/SCRAM auth on broker. | Consumer lag spikes. | Rebuild topics; replay from MinIO. |
| TM-06 | Norm. Worker | D, T | Worker crashes on malformed JSON payload. | Ingestion accepts massive payloads. | Med | Med | Pydantic strict typing; DLQ routing. | DLQ size alerts. | Fix schema; replay DLQ. |
| TM-07 | OpenSearch | I, D | Attacker queries unauthorized incident logs. | Exposed port 9200. | High | High | Network isolation (Docker bridge only). | Query volume spikes. | N/A (Preventative focused). |
| TM-08 | PostgreSQL | T, I, R | Attacker modifies audit logs. | Weak DB credentials. | Critical | High | Append-only logic; strong passwords. | Row count discrepancies. | Restore from daily backup. |
| TM-09 | Redis | D, I | Attacker clears rate-limit cache. | Exposed port 6379. | Med | Med | Network isolation; Redis auth. | Sudden traffic spikes. | Restart Redis (ephemeral). |
| TM-10 | MinIO | T, I | Attacker replaces raw log archives. | Compromised S3 credentials. | High | Low | Strong IAM policies; bucket versioning. | MinIO audit logs. | Restore previous version. |
| TM-11 | MLflow | T, I | Attacker views training parameters. | Unauthenticated UI. | Low | Low | Basic auth on MLflow server. | N/A | N/A |
| TM-12 | ML Inference | D | Model crashes on adversarial input. | Missing input normalization. | Med | Med | Strict tensor shape validation. | Worker restart loops. | Fallback to rule-based. |
| TM-13 | Agent Workflow | E, D | Agent loops infinitely consuming CPU. | Lack of graph execution limits. | High | Med | LangGraph `recursion_limit` set to 5. | Task timeout alerts. | Hard timeout kill switch. |
| TM-14 | Local LLM | I, D | LLM crashes (OOM) due to massive prompt. | unbounded RAG retrieval. | Med | High | Max token limits on context assembly. | Ollama crash logs. | Restart Ollama container. |
| TM-15 | RAG DB (OS) | T | Poisoned logs alter AI conclusions. | See TM-04 (Fake logs). | High | Med | Tagging synthetic/untrusted sources. | Analyst review. | Purge false logs. |
| TM-16 | Response Worker | E, T | Worker executes unapproved action. | Missing DB approval check in worker. | Critical| High | Worker explicitly checks `approval_id`.| Unauthorized action log. | Trigger rollback. |
| TM-17 | Audit Logging | R | Admin repudiates changing a rule. | Logging mechanism fails silently. | High | Med | Fail-closed logging middleware. | Missing logs in sequence. | Investigate API traces. |
| TM-18 | Monitoring (Grafana)| I | Attacker views SOC metrics. | Default admin/admin credentials. | Low | Low | Disable default logins; OIDC integration. | N/A | N/A |
| TM-19 | CI/CD | T, I | Malicious PR steals environment variables. | Secrets exposed to PR runners. | High | Low | GitHub protected branches & secret mgmt. | Workflow logs. | Rotate secrets globally. |
| TM-20 | Container Images | T | Base image contains vulnerable library. | Lack of scanning. | Med | Med | Trivy scanning in CI pipeline. | CVE scanner alerts. | Rebuild with patched base. |
| TM-21 | Kubernetes | E, D | Compromised pod escapes to node. | Container runs as root. | Critical| Low | `securityContext: runAsNonRoot`. | K8s audit logs. | Terminate pod; patch deployment. |
