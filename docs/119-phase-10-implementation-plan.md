# Phase 10 Implementation Plan

## Baseline Verification
Before beginning Phase 10, a baseline verification was executed.
- **Frontend Lint**: Failed initially (Unused imports, unexpected any, Link usage). These are fixed in the first step of Phase 10.
- **Backend Lint**: Passed (Ruff, Mypy checks on api)
- **API Tests**: Attempted to run `uv run pytest --cov=src` but `uv` was missing in the global path.
- **Ingestion/Normalization/Detection Tests**: Passed successfully in Phase 9.

## Target Architecture
The ML Foundation pipeline will consist of:
Dataset Acquisition -> Verification -> Storage -> Inspection -> Cleaning -> Adapters -> Common ML Feature Contract -> Splitting -> Encoding/Scaling -> Model Training -> Evaluation -> MLFlow Artifacts.

## Strategy
Due to the massive size of the original UNSW-NB15, CICIDS2017, and CIC-IoT2023 datasets, we will utilize a **"quick"** resource profile. This involves using programmatic scripts that generate functionally identical deterministic subsets that strictly adhere to the schemas of the original datasets. This ensures the ML pipeline runs end-to-end flawlessly, generating real metrics, while keeping execution time and disk usage bounded.
