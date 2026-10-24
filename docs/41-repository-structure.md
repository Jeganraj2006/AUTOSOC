# Repository Structure

## Directory Ownership

- `/apps/web`: The Next.js frontend application. Owned by the Frontend Team.
- `/apps/api`: The FastAPI backend control plane. Owned by the Backend Team.
- `/workers/*`: Independent background processing services. Owned by the Data Engineering / Backend Teams.
- `/packages/*`: Shared utilities and schemas. Types strictly flow *down* from here to apps and workers.
- `/ml/*`: Machine learning datasets, training scripts, and model artifacts. Owned by the Data Science Team.
- `/rules/*`: Authoritative security rules (Sigma) and Playbooks.
- `/infrastructure/*`: Deployment configurations (Docker/K8s/Monitoring).

## Dependency Rules
- **No Circular Dependencies**: `apps/api` cannot import from `workers/ingestion`. 
- **Shared Code**: Code that needs to be shared between two different workers MUST be moved to `packages/shared-python` or `packages/event-schemas`.
- **Frontend/Backend Separation**: `apps/web` interacts with `apps/api` exclusively over HTTP/REST.

## Test Locations
- **Unit Tests**: Reside adjacent to the code (e.g., `apps/api/tests`).
- **End-to-End Tests**: Reside in the root `/tests/end-to-end` directory using Playwright, treating the system as a black box.
