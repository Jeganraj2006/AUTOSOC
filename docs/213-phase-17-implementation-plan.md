# AutoSOC Phase 17 Implementation Plan
# Final Integration, Testing, Security Hardening, Deployment, Documentation, and Demonstration

## 1. Goal
Execute the final project phase to verify every subsystem, fix integrations, harden security, run complete end-to-end tests, establish production-style Kubernetes deployment, create robust CI/CD, prepare the final demo scenarios, and deliver comprehensive academic documentation. 

This phase transitions the system from a series of connected prototypes into a verifiable, integrated academic AutoSOC platform.

## User Review Required
> [!IMPORTANT]
> The final deployment relies on creating synthetic demo data, testing backup/restore procedures, running automated and manual validation scripts, and establishing Kubernetes manifests.
> - **Git Environment**: The project directory currently is not initialized as a git repository. Task 114 asks for Git Hygiene and Task 115 asks for a final commit. I will initialize the git repository during this phase. 
> - **CI/CD Tools**: To run tools like Semgrep, Trivy, and Gitleaks (Tasks 23-26), I will configure GitHub Actions workflows rather than installing them natively on Windows if the tooling is unavailable, OR provide local dockerized runs of these tools for local verification.
> - **Demo Mode vs Real execution**: Please confirm if you would like me to proceed with creating `scripts/setup-dev.ps1` and `scripts/demo/run_demo.py` that will interact heavily with your local docker stack, and whether the local stack has all prerequisites (PostgreSQL, Redpanda, Redis, MinIO, Keycloak, OpenSearch, MLflow) running and accessible via localhost.

## Open Questions
- **Kubernetes Cluster**: Task 69 mentions deploying to a local cluster if available. Do you have a local Kubernetes cluster (like Minikube, K3d, or Docker Desktop Kubernetes) running that you would like me to deploy to, or should I just validate the manifests using `kubeconform`/`helm lint`?
- **Load Testing**: For Task 52, is there a specific synthetic load tool (e.g., Locust, k6) you prefer to simulate the events and frontend traffic?

## Proposed Changes

### Phase A: Repository Audit & Clean-up (Tasks 1-4, 23-26, 114)
- **Inventory & Code Search**: Run searches across the codebase for `TODO`, `FIXME`, `pass`, `.skip` and resolve critical path placeholders.
- **Dependency Audit**: Review `pyproject.toml`, `package.json`, and Dockerfiles for unused or outdated libraries.
- **Security Scans**: Setup workflows/scripts to run Gitleaks for secret scanning, Semgrep for static analysis, and Trivy for container scanning. 
- **Git Initialization**: Run `git init`, add a `.gitignore`, and prepare a clean working tree.

### Phase B: Infrastructure, Resiliency & Clean Setup (Tasks 5-14, 27-32)
- **Setup Scripts**: Develop `scripts/setup-dev.ps1` to streamline infrastructure setup, migrations, and identity provisioning.
- **Environment Validation**: Create `scripts/validate-environment.py` to assert Docker, Python, ports, and memory configurations.
- **Backup & DB Integrity**: Implement a safe PG backup/restore script, run full Alembic up/down tests, and verify relational integrity of DB schemas. Verify Redpanda topics and OpenSearch index schemas.
- **Service Ordering & Failover**: Audit `docker-compose.yml` to enforce strict health-check-based startup ordering and test graceful worker shutdown.

### Phase C: Security Hardening (Tasks 3, 15-22, 100)
- **Auth & RBAC Matrix**: Formally test and lock down the 4 core roles in Keycloak/FastAPI.
- **API Security**: Configure Rate Limiting on critical endpoints, CORS, and IDOR testing for cross-tenant/cross-incident boundaries.
- **Frontend Security**: Implement robust Content-Security-Policy (CSP) headers in Next.js, verify no token leakage in localStorage, and check for XSS vectors in log rendering.

### Phase D: ML, RAG, and Agent Validation (Tasks 33-41, 42)
- **ML Artifacts**: Validate MLflow model hashes, dataset integrity checks (UNSW-NB15, etc.), and reproduce baseline metrics to confirm no data leakage. 
- **Agent Constraints**: Test prompt-injection defenses, ensure tools are scoped to read-only RAG/graph queries, and confirm the Agent has zero direct execution permissions.
- **Response Safety**: Validate that `analyst_approved_execution` rigorously checks for unexpired human approval records and that simulated lab execution behaves as expected.

### Phase E: E2E Testing, Performance & Load (Tasks 45-55, 97, 101)
- **E2E Traceability**: Validate the unbroken chain: Raw Event -> Normalized -> Detection -> Alert -> Incident -> ATT&CK -> Prediction -> Agent -> Response.
- **Automated Tests**: Polish the unit and integration test suites. Provide Playwright scripts for frontend testing.
- **Performance**: Run safe synthetic load tests (e.g., via Locust or custom script) to measure ingestion/detection/inference latencies (p50/p95). Resolve any discovered N+1 queries.

### Phase F: Observability & Kubernetes (Tasks 56-70)
- **Kubernetes Manifests**: Create `infrastructure/kubernetes/` containing Namespaces, Deployments, Services, ConfigMaps, Secrets, Ingress, NetworkPolicies, and Resource Limits. Run manifest validation.
- **Grafana & Prometheus**: Finalize dashboards covering system health, ML inference metrics, Agent executions, and Response tracking.

### Phase G: Documentation & Demo Support (Tasks 75-96, 106-113, 118)
- **Demo Scenarios**: Produce `scripts/demo/run_demo.py` covering Benign, Known Threat, Zero-Day Behavior, Attack Progression, and Human-Approved Response workflows.
- **Final Documentation**: Produce all mandatory `docs/214` to `docs/225` files (Architecture, User Guides, Demo Guide, Security Assessment, Release Notes).
- **Final README**: Completely rewrite the root `README.md` to be presentation-ready for the academic AutoSOC platform.

## Verification Plan

### Automated Tests
- `pytest -v --cov=autosoc_api` (Backend logic, RBAC, Models)
- `npm run test` (Frontend)
- Playwright UI E2E scripts
- Kubeconform / Helm lint for manifest validation

### Manual Verification
- Execute `scripts/demo/run_demo.py --scenario full_e2e` to visually verify data flows in the Next.js UI.
- Verify Grafana dashboards populate with metrics during load test.
- Check that Gitleaks/Trivy reports pass successfully.
