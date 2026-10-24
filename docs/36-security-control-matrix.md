# Security Control Matrix

| Control | Threat Mitigated | Component | Implementation Phase | Verification Method | Responsible |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OIDC Authentication** | Unauthorized Access | FastAPI, Next.js, Keycloak | Phase 5 | Unit Tests, E2E Login | Sec Architect |
| **RBAC / Scopes** | Privilege Escalation | FastAPI | Phase 5 | Unit Tests per route | Backend Eng |
| **TLS/HTTPS** | MitM, Sniffing | Ingress / API | Phase 17 (K8s) | Vulnerability Scan | Cloud Architect |
| **Pydantic Validation**| Injection, Malformed Data | FastAPI, Workers | Phase 5, 7 | Fuzzing, Unit Tests | Backend Eng |
| **OCSF Schema Val.** | Log Poisoning | Norm Worker | Phase 7 | Schema Tests | Data Eng |
| **Env Var Secrets** | Hardcoded Secrets | Docker / K8s | Phase 4 | Gitleaks (CI) | DevOps Eng |
| **Redis Rate Limiting**| DoS / Brute Force | FastAPI | Phase 5 | Load Testing | Backend Eng |
| **Immutable Audit Log**| Repudiation | Postgres, API | Phase 16 | Code Review | Sec Architect |
| **PII Masking** | Data Disclosure | Norm Worker | Phase 7 | Regex Unit Tests | Data Eng |
| **Prompt Delimiters** | Prompt Injection | Agent Worker | Phase 15 | AI Red Teaming | AI Sec Eng |
| **Tool Allowlisting** | Agent Tool Misuse | Agent Worker | Phase 15 | Code Review | AI Sec Eng |
| **Human Approval** | Unauthorized Actions | Response Worker | Phase 16 | E2E Tests | Sec Architect |
| **Action Rollback** | Disruption of Service| Response Worker | Phase 16 | Integration Tests | Sec Architect |
| **Trivy Scanning** | Container Vulns | CI/CD | Phase 3 | GitHub Actions | DevOps Eng |
| **Semgrep Scanning** | Code Vulnerabilities| CI/CD | Phase 3 | GitHub Actions | DevOps Eng |
| **Network Policies** | Lateral Movement | Kubernetes | Phase 17 | Manifest Review | Cloud Architect |
| **Automated Backups** | Data Loss / Ransomware| Postgres, MinIO | Phase 17 | Restore Drill | Cloud Architect |
| **MLflow Model Hash** | Model Tampering | ML Worker | Phase 10 | Hash verification | ML Eng |
| **OTel Monitoring** | Unnoticed Outages | All Components | Phase 4, 17 | Chaos Engineering | DevOps Eng |
| **Dead-Letter Queues** | Silent Data Loss | Redpanda, Workers | Phase 7 | Integration Tests | Data Eng |
