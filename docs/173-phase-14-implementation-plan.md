# Phase 14: Attack Progression Prediction Implementation Plan

## Goal Description
Implement an Agentic AI-driven Attack Progression Prediction engine. This phase focuses on building a software+ML pipeline that forecasts the likely next step in an attack progression (based on MITRE ATT&CK techniques) without claiming absolute certainty. We will build empirical transition matrices, a Markov chain baseline, and LSTM/Transformer deep learning predictors.

The resulting prediction engine will consume data from incidents, technique graphs, and timelines to yield a calibrated `PredictionResult` with a list of top-K probable next techniques, which is then fed back to the frontend for SOC analysts to review.

## Proposed Changes

### [ML Progression Models (`ml/progression`)]
We will implement the training datasets, baseline transition algorithms, and sequence models using the existing PyTorch & MLflow infrastructure.

- `ml/progression/models/markov.py`
- `ml/progression/models/lstm.py`
- `ml/progression/models/transformer.py`
- `ml/progression/features/builder.py`
- `ml/progression/training/loop.py`

### [Prediction Worker & Message Queue (`workers/prediction/`)]
A standalone prediction microservice that consumes trigger events and generates predictions asynchronously.

- `workers/prediction/src/autosoc_prediction/consumer.py`
- `workers/prediction/src/autosoc_prediction/predictor.py`
- `workers/prediction/src/autosoc_prediction/publisher.py`

### [FastAPI Backend (`apps/api/src/autosoc_api/`)]
Update the core API to persist, manage, and serve predictions for the frontend UI.

- `apps/api/src/autosoc_api/db/models/prediction.py`
- `apps/api/src/autosoc_api/api/v1/endpoints/predictions.py`

### [SOC Frontend (`apps/web/src/`)]
Implement the visualization components to allow analysts to see the attack forecast without confusing it with observed evidence.

- `apps/web/src/components/soc/prediction-panel.tsx`
- `apps/web/src/components/soc/attack-graph.tsx`

## Verification Plan

### Automated Tests
- Pytest for progression baselines and LSTM.
- Automated leakage tests.

### Manual Verification
1. **Scenario 1 - Authentication**: Emit a sequence of Repeated Login Failures -> Valid Account Usage -> Privilege Change.
2. **Scenario 2 - Network/Endpoint**: Reconnaissance -> Suspicious Process.
3. **Historical Replay Evaluation**: Mask future techniques in a controlled sequence and predict.
