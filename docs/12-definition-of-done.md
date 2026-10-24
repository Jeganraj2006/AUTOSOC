# Definition of Done (DoD)

To ensure high software quality, security, and maintainability, all tasks, user stories, and epics must meet the following criteria before being marked as "Done".

## 1. Global Definition of Done
- Code passes all automated tests.
- Code has been peer-reviewed (or self-reviewed with a formal checklist if working solo).
- No hardcoded secrets (API keys, passwords, tokens) exist in the codebase.
- The feature branch is merged into the main branch cleanly.
- The project runs reproducibly on a fresh machine following the documented setup steps.

## 2. Documentation Definition of Done
- The feature is documented in the project README or a specific Markdown file in the `docs/` directory.
- Any architectural changes are reflected in the system design diagrams.
- API endpoints are documented using OpenAPI/Swagger.
- Acceptance criteria from the User Story are explicitly verified in the documentation.

## 3. Backend Feature Definition of Done
- Unit tests exist and pass (aiming for >80% coverage).
- Input validation is implemented (e.g., using Pydantic).
- Proper error handling is implemented (no silent failures or unhandled stack traces returned to the client).
- Audit logging is implemented for any state-changing actions.
- Database schema changes are managed via Alembic migration scripts.

## 4. Frontend Feature Definition of Done
- UI components are responsive and follow the Tailwind CSS / shadcn/ui design system.
- Component tests or E2E tests (Playwright) verify the critical user path.
- The UI handles loading states, empty states, and error states gracefully.
- No sensitive data is logged to the browser console.

## 5. Machine Learning Feature Definition of Done
- Model training code is versioned and reproducible.
- Training runs, parameters, and metrics are logged in MLflow.
- The model achieves the minimum acceptable metrics defined in the Success Metrics document.
- Inference API includes validation for unexpected inputs (e.g., null values, extreme outliers).

## 6. Agentic AI Feature Definition of Done
- LangGraph workflows include failure handling (e.g., API timeouts).
- Prompts are stored in configuration files or a database, not hardcoded deep in logic.
- The agent's output is sanitized before being displayed to the user.
- The agent's actions strictly adhere to the safety policy (no autonomous destructive actions).

## 7. Security Feature Definition of Done
- Static Application Security Testing (SAST) tools (e.g., Semgrep) return no critical/high vulnerabilities.
- Secret scanning (e.g., Gitleaks) passes successfully.
- Container image scanning (e.g., Trivy) passes with no unmitigated critical CVEs.
- Role-Based Access Control (RBAC) is enforced at the API route level.

## 8. Deployment Definition of Done
- Docker Compose configuration is updated and tested.
- Kubernetes manifests (if applicable to the phase) are updated and apply without errors.
- Application metrics (OpenTelemetry) are exposed and scrapeable by Prometheus.
- Infrastructure configurations do not rely on local-machine specific absolute paths.
