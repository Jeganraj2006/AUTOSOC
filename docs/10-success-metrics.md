# Success Metrics

## 1. Detection Metrics
| Metric | Target | Minimum Acceptable | Hardware/Dataset Dependent |
| :--- | :--- | :--- | :--- |
| Precision | 0.90 | 0.75 | Yes (Dataset quality) |
| Recall | 0.85 | 0.70 | Yes (Dataset quality) |
| F1 Score | 0.87 | 0.72 | Yes (Dataset quality) |
| PR-AUC (Precision-Recall AUC) | 0.90 | 0.80 | Yes (Dataset quality) |
| False-Positive Rate | < 5% | < 15% | Yes (Dataset quality) |
| False-Negative Rate | < 15% | < 30% | Yes (Dataset quality) |
| Detection Latency | < 2 seconds | < 10 seconds | No (System architecture) |

## 2. Prediction Metrics
| Metric | Target | Minimum Acceptable | Hardware/Dataset Dependent |
| :--- | :--- | :--- | :--- |
| Top-1 Accuracy (Next technique) | > 60% | > 40% | Yes (Dataset variance) |
| Top-3 Accuracy (Next technique) | > 85% | > 65% | Yes (Dataset variance) |
| Prediction Lead Time | Generated instantly on incident creation | Generated within 5s | No |
| Confidence Calibration | Confidence score matches actual empirical accuracy | Soft requirement | Yes (Model tuning) |
| Attack-Path Coverage | Maps 80% of MITRE techniques in dataset | 50% mapping | Yes (Rule tagging) |

## 3. Platform Metrics
| Metric | Target | Minimum Acceptable | Hardware/Dataset Dependent |
| :--- | :--- | :--- | :--- |
| Event Throughput | 2,000 EPS | 500 EPS | Yes (Hardware CPU/RAM) |
| API Response Time (P95) | < 200 ms | < 800 ms | Yes (Hardware CPU) |
| Search Latency (P95) | < 1 second | < 5 seconds | Yes (Storage IOPS) |
| Queue Lag | 0 (Processing matches ingestion) | < 60 seconds backlog | Yes (Worker scaling) |
| Service Health | 99.9% Uptime during testing | 95.0% Uptime | No |
| Error Rate (HTTP 5xx) | < 0.1% | < 1.0% | No |

## 4. SOC Workflow Metrics
| Metric | Target | Minimum Acceptable | Hardware/Dataset Dependent |
| :--- | :--- | :--- | :--- |
| Mean Time to Detect (MTTD) | < 10 seconds | < 1 minute | No |
| Mean Time to Investigate (MTTI) | < 1 minute (AI assisted) | < 5 minutes | Yes (LLM Inference speed) |
| Mean Time to Recommend Response | < 30 seconds post-investigation | < 2 minutes | Yes (LLM Inference speed) |
| Alert-to-Incident Correlation Quality | > 90% related alerts grouped correctly | > 70% | No |
| Analyst Approval Traceability | 100% of actions logged | 100% | No (Mandatory) |

## 5. Agentic AI Metrics
| Metric | Target | Minimum Acceptable | Hardware/Dataset Dependent |
| :--- | :--- | :--- | :--- |
| Evidence Citation Rate | 100% of claims cite a log ID | 90% | Yes (LLM adherence) |
| Unsupported-Claim Rate (Hallucinations)| 0% | < 5% | Yes (LLM adherence) |
| Tool-Call Success Rate | > 95% | > 80% | No |
| Policy-Violation Rate (Unsafe actions) | 0% (Strictly enforced) | 0% | No (Mandatory) |
| Human Override Rate (Rejected actions) | < 10% | < 30% | Yes (Recommendation quality) |
