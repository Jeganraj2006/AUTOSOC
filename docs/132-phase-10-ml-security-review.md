# ML Security Review (Phase 10)

## Authenticity & Download Safety
- Dataset download URLs point to official academic sites (e.g., `research.unsw.edu.au`, `unb.ca`).
- Synthetically generated subsets used in the pipeline explicitly announce themselves to prevent confusion with the full production benchmark datasets.

## Integrity
- SHA-256 checksums are calculated and verified upon acquisition, ensuring no accidental file corruption or tampering.

## Preprocessing Risks
- Dataframes explicitly handle `NaN` and infinite numeric values.
- Identifiers and non-essential strings are pruned before the ML pipelines, nullifying arbitrary code execution via manipulated category fields (e.g., in categorical encoders).
- Scikit-learn's `StandardScaler` does not deserialize untrusted data; however, loading the scaler and models strictly relies on MLflow's controlled MLmodel format and authenticated S3/MinIO/Local artifacts.

## Pickle / Joblib Deserialization
**WARNING**: `joblib.load()` and `torch.load()` are used for artifact loading. These are inherently insecure against malicious payloads. 
**Mitigation**: ML model artifacts are strictly isolated in MinIO (or locally in `mlruns.db`) and are immutable. Only authenticated CI pipelines are permitted to publish these files, restricting the attack vector.
