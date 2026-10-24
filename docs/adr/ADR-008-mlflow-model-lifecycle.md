# ADR-008: MLflow for Model Lifecycle

## Status
Accepted

## Context
The ML-inference worker relies on models (e.g., PyTorch, scikit-learn) trained to detect anomalies. Managing model versions, tracking hyperparameters, and deploying the correct model artifact manually is error-prone and violates reproducibility requirements (NFR-AI-001).

## Decision
We will use MLflow to track experiments, register models, and serve as the model artifact repository. MinIO will be used as the backend artifact store for MLflow.

## Alternatives Considered
- **Weights & Biases (WandB)**: Rejected because it is a SaaS platform, and we require a locally deployable solution for the academic environment.
- **Manual Pickle/PTH files in Git**: Rejected because large binaries bloat the repository, and versioning lacks metadata (metrics, hyperparameters).

## Positive Consequences
- Standardized model registry.
- Easy rollback to previous model versions if model drift occurs.
- API-driven fetching of the latest production model by the ML-inference worker on startup.

## Negative Consequences
- Adds operational overhead to the deployment stack (MLflow server + MinIO backend).

## Security Implications
- Model artifacts must be protected from tampering. By centralizing them in MLflow/MinIO, we can enforce access controls better than arbitrary files on a shared filesystem.

## Revisit Conditions
- N/A; MLflow is the standard open-source MLOps platform.
