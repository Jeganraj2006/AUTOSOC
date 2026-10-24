# ADR-011: Docker Compose Before Kubernetes

## Status
Accepted

## Context
AutoSOC requires a complex infrastructure stack (PostgreSQL, OpenSearch, Redpanda, Redis, MinIO, Keycloak, FastAPI, Next.js). Jumping straight to Kubernetes for local development introduces a steep learning curve and high resource overhead that slows down rapid iteration.

## Decision
We will use Docker Compose as the primary deployment mechanism for local development and the MVP demonstration. Kubernetes manifests will be generated only as documentation for a production-style deployment architecture in Phase 17.

## Alternatives Considered
- **Minikube / K3s (Local Kubernetes)**: Rejected for the primary development workflow due to the complexity of managing local persistent volumes, ingresses, and registry synchronization during fast iteration.
- **Bare Metal / Native Installs**: Rejected because it violates the portability requirement (NFR-MAINT-002).

## Positive Consequences
- Rapid setup for new developers (`docker-compose up`).
- Easier networking between containers locally.
- Lower overhead than running a full K8s control plane locally.

## Negative Consequences
- The Docker Compose configuration will not directly translate to production, requiring a separate set of manifests (Helm/Kustomize) to be maintained.

## Security Implications
- Secrets management in Docker Compose (usually `.env` files) is less secure than Kubernetes Secrets or HashiCorp Vault. These `.env` files must be strictly excluded from version control.

## Revisit Conditions
- N/A; Kubernetes documentation is explicitly deferred to the end of the project.
