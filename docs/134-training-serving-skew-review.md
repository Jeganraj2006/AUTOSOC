# Training-Serving Skew Review

## Objective
Ensure features engineered in Phase 10 (Training) can be deterministically reproduced from live Kafka streams (`security.events.enriched`) in Phase 11 (Serving).

## Findings
The subset of 7 features defined in the Common Feature Contract (`duration`, `proto_tcp`, `proto_udp`, `fwd_pkts`, `bwd_pkts`, `fwd_bytes`, `bwd_bytes`) perfectly aligns with the `NetworkContext` sub-schema of the AutoSOC EnrichedSecurityEvent.

- **Units**: Both training and serving use seconds for `duration` and raw integer counts for bytes/packets.
- **Handling Missing Values**: Both environments fall back to median/zero imputation strategies.
- **Feature Scaling**: The fitted `StandardScaler` artifact saved via `joblib` can be seamlessly loaded by the production ML Inference worker, ensuring identical transformation mechanics.
- **Label Leakage**: Real-world events do not have `.label` tags. The pipeline strictly drops all identifiers and labels prior to any transformations, confirming zero dataset-only label leakage is carried to production.

## Conclusion
The Common Feature Contract is **approved** for Phase 11 production hybrid ML detector usage. No discrepancies found.
