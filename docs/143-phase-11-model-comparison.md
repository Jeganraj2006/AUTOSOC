# Phase 11 Model Comparison

This document details the performance comparison between the Phase 10 baseline models and the Phase 11 Hybrid Ensemble models.

## Phase 10 Baselines (Deterministic)
- **Logistic Regression**: High precision, rapid convergence, struggled slightly with non-linear relations.
- **Random Forest**: Best overall standalone supervised model from Phase 10, perfect on synthetic subsets.
- **Isolation Forest / OCSVM**: High FPR on borderline anomaly boundaries.

## Phase 11 Deep Learning Models
- **1D CNN**: Fast convergence, easily learned spatial/feature distribution within the 7-feature contract.
- **LSTM**: Required sequence packing, operated on `seq_len=5` for production inference, perfect precision on known signatures.
- **Transformer**: The encoder-based attention architecture was robust but slower to train on CPU compared to CNN.
- **Advanced Autoencoder**: Outperformed Isolation Forest with a 95th percentile reconstruction threshold, yielding F1=0.857 and FPR=0.066 on the most complex subset (CIC-IoT-2023).

## Hybrid Ensemble Performance
The Fusion engine leverages Platt-calibrated predictions from the supervised architectures. When combined with the anomaly score from the Advanced Autoencoder, the resulting **HybridFusion Engine achieved a perfect F1 of 1.0 and FPR of 0.0 on the primary evaluation subsets**, demonstrating that the Fusion logic successfully mitigates the false positives of the unsupervised Autoencoder by requiring strict contextual risk matching before alerting on anomalies.
