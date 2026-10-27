# Technology stack

| Area | Implemented technology |
| --- | --- |
| UI | Next.js 16.4.1, React 19.2, TypeScript, TanStack Query, Vitest, Playwright |
| API | Python 3.12, FastAPI, Pydantic, SQLAlchemy async, Alembic, PyJWT |
| Identity | Keycloak 22.0.1, Authorization Code + PKCE through Auth.js/NextAuth |
| State | PostgreSQL 15, Redis 7 Alpine, Redpanda v26.2.6, OpenSearch 2.11.0 |
| Object storage | SeaweedFS `chrislusf/seaweedfs:4.50` pinned to the Compose digest |
| AI/ML | Local Ollama `llama3.2:3b`, deterministic rule/correlation/prediction code, LangGraph-oriented workflow source |

Image tags are pinned where Compose currently specifies them; PostgreSQL, Redis, Keycloak, and OpenSearch remain tag-pinned rather than digest-pinned. This is acceptable only for the stated local-development scope.
