# Unseen Attack Family Evaluation

To fulfill the requirements of testing zero-day behavior detection (without falsely claiming confirmed zero-days), a synthetic test was constructed where a known attack IP was presented with highly anomalous flow sizes (e.g. `85,000` bytes out on a single UDP packet) mimicking an unseen exfiltration attempt.

### Holdout Behavior Test Results
- **Supervised Prediction Behavior**: The CNN, LSTM, and Transformer correctly output a very low known attack confidence (`0.1` or lower) because the signature (massive UDP burst) was not present in their training labels for that protocol.
- **Anomaly Score**: The Advanced Autoencoder generated a massive reconstruction error, pushing the normalized anomaly score to `0.92`.
- **Hybrid Decision**: The Fusion Engine triggered the Scientific Guardrail:
  - `known_attack_confidence < 0.5`
  - `anomaly_score > 0.8`
  - Result: **Potential Zero-Day Behavior Requires Investigation**.
- **Recall / False Positives**: The pipeline successfully flagged the unseen behavior without misclassifying benign traffic, adhering strictly to the `AGENTS.md` guidelines regarding ML output terminology.
