# Project Epics

## Epic 1: Requirements and Project Planning
- **Objective**: Define project scope, requirements, risks, and success metrics.
- **Included Features**: Architecture planning, threat modelling, documentation generation.
- **Dependencies**: None.
- **Expected Deliverables**: Phase 1 markdown documentation (Requirements, Scope, Use Cases, MVP definition).
- **Completion Criteria**: All Phase 1 documentation is created, reviewed, and approved.

## Epic 2: Architecture and Threat Modelling
- **Objective**: Design the system architecture and identify security threats.
- **Included Features**: System design diagrams, data flow diagrams, STRIDE threat model.
- **Dependencies**: Epic 1.
- **Expected Deliverables**: Architecture diagrams, threat model report.
- **Completion Criteria**: Threat model identifies mitigations for core components.

## Epic 3: Repository and Development Setup
- **Objective**: Initialize version control, linting, and CI/CD pipelines.
- **Included Features**: Git repository, GitHub Actions (tests, security scans like Semgrep/Trivy), Prettier/ESLint/Ruff configuration.
- **Dependencies**: Epic 1.
- **Expected Deliverables**: Configured repository with passing baseline CI.
- **Completion Criteria**: PRs require passing tests and linting.

## Epic 4: Local Infrastructure
- **Objective**: Provision local development databases and messaging systems.
- **Included Features**: Docker Compose for PostgreSQL, OpenSearch, Redpanda, Redis, MinIO, Keycloak.
- **Dependencies**: Epic 2.
- **Expected Deliverables**: `docker-compose.yml` and initialization scripts.
- **Completion Criteria**: `docker-compose up` successfully starts all infrastructure services.

## Epic 5: Authentication and Core Backend
- **Objective**: Implement OIDC authentication and the baseline FastAPI application.
- **Included Features**: Keycloak realm configuration, FastAPI setup, SQLAlchemy ORM, Alembic migrations, RBAC middleware.
- **Dependencies**: Epic 3, Epic 4.
- **Expected Deliverables**: Secure API with user login and role validation.
- **Completion Criteria**: Unauthorized requests are rejected; DB migrations run successfully.

## Epic 6: Log Ingestion
- **Objective**: Build the service to receive and queue security events.
- **Included Features**: Endpoints for Syslog, Windows logs, CloudTrail, k8s audit. Synthetic log generator. Redpanda producer.
- **Dependencies**: Epic 5.
- **Expected Deliverables**: Ingestion worker parsing raw logs into Kafka topics.
- **Completion Criteria**: Synthetic generator successfully pumps 1000 EPS into Redpanda.

## Epic 7: Event Normalization and Enrichment
- **Objective**: Process raw events into a standardized schema.
- **Included Features**: Redpanda consumer, OCSF mapping logic, OpenSearch indexing, deduplication.
- **Dependencies**: Epic 6.
- **Expected Deliverables**: Background worker that reads from topics and writes normalized JSON to OpenSearch/Postgres.
- **Completion Criteria**: Searchable, normalized logs appear in OpenSearch.

## Epic 8: SOC Frontend
- **Objective**: Build the React/Next.js analyst dashboard.
- **Included Features**: Login screen, alerts table, incident view, basic search UI using shadcn/ui and Tailwind.
- **Dependencies**: Epic 5.
- **Expected Deliverables**: Functional web application consuming the FastAPI backend.
- **Completion Criteria**: Analyst can log in and view a populated table of events.

## Epic 9: Rule-Based Detection
- **Objective**: Implement deterministic threat detection using Sigma rules.
- **Included Features**: Sigma rule parser, matching engine against normalized events, alert generation in DB.
- **Dependencies**: Epic 7.
- **Expected Deliverables**: Detection worker generating alerts for known malicious patterns.
- **Completion Criteria**: Triggering a known malicious synthetic log generates an Alert record.

## Epic 10: Dataset and ML Foundation
- **Objective**: Prepare ML models for anomaly detection.
- **Included Features**: Data preprocessing, PyTorch/scikit-learn model training scripts, MLflow integration.
- **Dependencies**: Epic 7.
- **Expected Deliverables**: Trained baseline model, MLflow server running via Docker.
- **Completion Criteria**: Model achieves >80% accuracy on the test set and is logged in MLflow.

## Epic 11: Hybrid Zero-Day Detection
- **Objective**: Integrate ML anomaly detection into the event pipeline.
- **Included Features**: ML Inference API, flagging high-confidence anomalies as "potential zero-day behavior".
- **Dependencies**: Epic 9, Epic 10.
- **Expected Deliverables**: Real-time scoring of events; alerts generated for unseen anomalies.
- **Completion Criteria**: System successfully flags anomalous synthetic events missed by Sigma rules.

## Epic 12: Alert Correlation and Incident Management
- **Objective**: Group related alerts into actionable incidents.
- **Included Features**: Correlation engine (time/entity based), incident database tables, evidence preservation logic, incident UI.
- **Dependencies**: Epic 8, Epic 11.
- **Expected Deliverables**: Incidents appearing in the dashboard containing multiple related alerts.
- **Completion Criteria**: 5 related alerts are automatically merged into 1 incident.

## Epic 13: MITRE Mapping and Attack Graph
- **Objective**: Visualize the attack utilizing MITRE ATT&CK.
- **Included Features**: Tactic/Technique mapping logic, Cytoscape.js UI integration.
- **Dependencies**: Epic 12.
- **Expected Deliverables**: Interactive graph on the Incident page showing nodes (assets) and edges (techniques).
- **Completion Criteria**: Graph renders correctly based on incident alert data.

## Epic 14: Attack-Progression Prediction
- **Objective**: Predict the attacker's next move.
- **Included Features**: Sequence modeling (e.g., Markov Chain or simple LSTM), prediction API.
- **Dependencies**: Epic 13.
- **Expected Deliverables**: UI displays "Likely Next Step" based on current graph sequence.
- **Completion Criteria**: Given techniques A and B, system predicts technique C.

## Epic 15: Agentic AI Investigation and RAG
- **Objective**: Implement LangGraph workflows for autonomous investigation.
- **Included Features**: Ollama local integration, LangGraph orchestrator, OpenSearch RAG tool, LLM summarization.
- **Dependencies**: Epic 12.
- **Expected Deliverables**: Agent autonomously queries logs and adds a summary to the incident.
- **Completion Criteria**: Agent successfully cites log evidence in its technical summary.

## Epic 16: Response Playbooks and Approval
- **Objective**: Implement safe, human-approved containment.
- **Included Features**: Playbook definitions, dry-run simulation API, Analyst approval/rejection UI, rollback logic.
- **Dependencies**: Epic 15.
- **Expected Deliverables**: Incident page shows recommendations with "Simulate" and "Approve" buttons.
- **Completion Criteria**: Approval triggers an audit log and mock execution; rollback reverses the state.

## Epic 17: Testing, Deployment, and Documentation
- **Objective**: Finalize the project for production-style deployment.
- **Included Features**: Kubernetes manifests (Helm/Kustomize), final E2E testing (Playwright), performance benchmarking, user manuals.
- **Dependencies**: All prior Epics.
- **Expected Deliverables**: Deployable K8s configuration and comprehensive final report.
- **Completion Criteria**: System successfully deploys to Minikube/K3s and passes all E2E tests.
