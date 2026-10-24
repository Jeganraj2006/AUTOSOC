# ML Security Review (Phase 11)

## Architecture Overview
The Phase 11 Hybrid ML Inference Pipeline introduces Deep Learning and unsupervised models directly into the primary streaming path (`security.events.enriched`).

## Risks Assessed and Mitigated
1. **Malicious Pickle Payloads (Model Artifact Integrity)**
   - *Risk*: PyTorch `.pkl` or standard model checkpoints can execute arbitrary code during deserialization. 
   - *Mitigation*: The `MLInferenceWorker` only loads validated MLflow runs from the local `sqlite:///mlruns.db` store that were generated during Phase 10/11. The models are not exposed to an upload endpoint.
2. **Denial of Service via Sequence Exhaustion**
   - *Risk*: An attacker flooding events with randomly generated IPs could cause unbounded memory growth in the `SequenceBuilder`.
   - *Mitigation*: The sequence state buffer utilizes a hard boundary (`max_seq_len=5`). A production Redis implementation will employ a strict TTL and max-size eviction policy per entity to prevent memory overflow.
3. **Training-Serving Skew & NaN Handling**
   - *Risk*: Malformed float properties could cause PyTorch tensors to become `NaN` or `inf`, crashing the process.
   - *Mitigation*: The `production_feature_set.yaml` ensures only strongly typed features are mapped. We use PyTorch `Tensor` casting and the schemas enforce constraints prior to model evaluation.
4. **Adversarial Evasion**
   - *Risk*: An attacker crafts traffic perfectly aligned to mimic the `benign` feature boundaries.
   - *Mitigation*: The hybrid approach ensures deterministic Sigma rules (Phase 9) remain active. The ML layer supplements rule gaps.
