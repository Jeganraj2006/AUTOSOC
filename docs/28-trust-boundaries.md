# Trust Boundaries

```mermaid
graph TD
    subgraph Public Internet
        User[User Browser]
        Intel[Threat Intel API]
    end

    subgraph Corporate Network
        Source[Security Log Sources]
    end

    subgraph AutoSOC Platform Boundary
        Ingress[API Gateway/Ingress]
        
        subgraph Web/App Boundary
            UI[Next.js UI]
            API[FastAPI Control Plane]
        end
        
        subgraph Auth Boundary
            IAM[Keycloak]
        end
        
        subgraph Data Services Boundary
            DB[(PostgreSQL)]
            OS[(OpenSearch)]
            RP((Redpanda))
            Cache[(Redis)]
        end
        
        subgraph AI/ML Boundary
            ML[ML Inference Worker]
            Agent[Agent Worker]
            LLM[Ollama Local LLM]
        end
        
        subgraph Execution Boundary
            Resp[Response Worker]
        end
    end

    User -->|HTTPS| Ingress
    Ingress --> UI
    Ingress --> API
    Source -->|TLS| Ingress
    API --> IAM
    UI --> IAM
    API <--> Data Services Boundary
    ML <--> Data Services Boundary
    Agent <--> Data Services Boundary
    Agent --> LLM
    Agent --> Intel
    Resp -->|Executes Action| Source
```

## Boundary Definitions

### Public Ingress Boundary
- **Data Entering**: HTTP requests, raw security logs (if external).
- **Authentication**: OIDC Tokens for UI, API keys/mTLS for log sources.
- **Main Threats**: DDoS, unauthorized access, malformed payloads.
- **Controls**: WAF, Rate Limiting (Redis), Pydantic schema validation.

### Data Services Boundary
- **Data Entering**: Processed logs, database queries.
- **Authentication**: Internal network credentials (Postgres User/Pass).
- **Main Threats**: SQL Injection, unauthorized data access by compromised workers.
- **Controls**: ORM (SQLAlchemy) prevents SQLi; network isolation (internal Docker network).

### AI/ML Boundary
- **Data Entering**: Normalized logs for inference; prompts containing logs for LLM.
- **Data Leaving**: Anomaly scores, LLM generated text.
- **Main Threats**: Prompt Injection, Model Poisoning.
- **Controls**: Strict input masking (PII removal) before LLM generation. Output is treated as untrusted and requires human approval.

### Execution Boundary (Response Worker)
- **Data Entering**: Analyst-approved action tasks.
- **Data Leaving**: Commands to external infrastructure.
- **Main Threats**: Unauthorized execution, Lateral movement if worker is compromised.
- **Controls**: Execution worker is isolated; requires explicit cryptographic approval record from the database to run.
