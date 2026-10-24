# Baseline Model Cards

## AutoSOC Determinstic Baselines

### Model Description
- **Task**: Binary Classification (Attack vs Benign)
- **Algorithms**: Logistic Regression, Random Forest, Isolation Forest, OCSVM, Autoencoder.
- **Input Modality**: Numerical Network Flow Features
- **Output**: Binary Int (0 for Benign, 1 for Attack)

### Training Data
- **Datasets**: UNSW-NB15, CICIDS2017, CIC-IoT2023
- **Preprocessing**: Median imputation, scaling via StandardScaler, strictly stratified splits.

### Evaluation Data
- Data explicitly separated into 70% Train, 15% Validation, 15% Test.

### Metrics & Thresholds
- **Threshold**: Standard 0.5 probability (Supervised), or 95th Percentile of Benign Reconstruction Error (Autoencoder).
- **Primary Metric**: F1-Score to balance Precision (reducing alert fatigue) and Recall (catching true attacks).

### Limitations
- **Concept Drift**: Network baselines change, requiring periodic re-training.
- **Payload Blindness**: Uses metadata only; payloads are ignored, potentially missing zero-byte payload exploitation vectors.
