# ADR-002: FastAPI for Control-Plane Backend

## Status
Accepted

## Context
AutoSOC requires a high-performance backend API to serve the Next.js frontend, manage background workers, and orchestrate ML/AI workflows. The project relies heavily on Python ecosystem tools for Machine Learning (PyTorch, scikit-learn) and AI (LangGraph). 

## Decision
We will use FastAPI (Python) as the framework for the control-plane API and the foundation for background workers.

## Alternatives Considered
- **Django**: Rejected because AutoSOC is heavily API-driven rather than template-driven, and FastAPI's async support is superior for high-concurrency tasks.
- **Node.js/Express**: Rejected because integrating seamlessly with Python-based ML/AI libraries would require complex cross-language communication (e.g., gRPC) for core logic.
- **Go**: Rejected because it lacks the mature ecosystem for ML and LLM orchestration that Python provides.

## Positive Consequences
- Native async/await support for high-throughput I/O operations.
- Built-in data validation and serialization via Pydantic.
- Automatic OpenAPI documentation generation.
- Seamless integration with the Python ML/AI ecosystem.

## Negative Consequences
- Python's Global Interpreter Lock (GIL) may limit CPU-bound performance within a single process (mitigated by using multiple worker processes).

## Security Implications
- Strong input validation provided by Pydantic reduces the risk of injection attacks and malformed payloads.

## Revisit Conditions
- If the control plane encounters severe performance bottlenecks related to Python's execution speed, we may extract specific high-throughput endpoints into Go or Rust services.
