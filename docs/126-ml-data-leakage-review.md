# ML Data Leakage Review

## Findings
During preprocessing of the generated subset datasets, the following leakage vectors were analyzed and controlled:
- **Identifier Columns**: Removed arbitrary identifiers (like IP addresses and row indices) to prevent the model from memorizing specific hosts rather than behavior.
- **Future Information**: Dropped columns that exist only post-event (like the explicit textual `attack_cat` class strings) before training.
- **Temporal Ordering**: Stratified splitting with fixed seeds is utilized. Time-series leakage is mitigated by ignoring explicit `timestamp` columns in the models.
- **Duplicate Rows**: Detected and handled identically across splits to prevent train/test overlap leakage.

## Data Quality Gates
Automated assertions exist in the preprocessing pipeline to ensure no identifier strings or categorical labels slip into the `X_train` numerical matrices.
