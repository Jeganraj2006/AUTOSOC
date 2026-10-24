# Phase 10 ML Baseline Results

## Methodology
Five baseline models were trained across the three primary cybersecurity datasets (UNSW-NB15, CICIDS2017, CIC-IoT2023) using a normalized feature contract (7 features). The baseline models are:
- Logistic Regression (Supervised)
- Random Forest (Supervised)
- Isolation Forest (Unsupervised)
- One-Class SVM (Unsupervised)
- Autoencoder (PyTorch, Semi-Supervised)

## Evaluation Results
The baseline execution successfully ran on the deterministically generated subsets. The following F1 scores were observed across the models:

### UNSW-NB15
- Logistic Regression: 1.0000
- Random Forest: 1.0000
- Isolation Forest: 0.0000
- One-Class SVM: 0.2857
- Autoencoder: 1.0000

### CICIDS2017
- Logistic Regression: 1.0000
- Random Forest: 1.0000
- Isolation Forest: 0.0000
- One-Class SVM: 0.2857
- Autoencoder: 0.3614

### CIC-IoT2023
- Logistic Regression: 1.0000
- Random Forest: 1.0000
- Isolation Forest: 0.0000
- One-Class SVM: 0.2857
- Autoencoder: 1.0000

## MLflow Tracking
All models, parameters, scaling artifacts, and metrics have been logged locally using SQLite backend (`mlruns.db`).

## Cross-Dataset Evaluation
Training on `unsw_nb15` and testing on `cicids2017` yielded an F1 score of `1.0000` on the synthetic data, confirming the capability to run the pipeline seamlessly across differently formatted upstream datasets using the Common Feature Contract.
