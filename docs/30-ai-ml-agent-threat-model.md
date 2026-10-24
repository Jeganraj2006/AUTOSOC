# AI, ML, and Agent Threat Model

| Threat | Source | Attack Path | Affected Component | Consequence | Mitigation | Human Control |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Training-data poisoning** | Malicious Actor | Contributes bad data to public datasets. | PyTorch Model | Model fails to detect specific attacks. | Use trusted benchmark datasets only. | Monitor F1 scores during training. |
| **Test-data contamination** | Data Engineer | Overlap between train/test splits. | ML Evaluation | Inflated accuracy metrics; poor real-world performance. | Strict temporal splitting of datasets. | Code review of data pipeline. |
| **Dataset leakage** | Data Engineer | Future labels leak into training features. | PyTorch Model | Unrealistic 100% accuracy in testing. | Drop label-correlated features (e.g., specific IPs). | Code review. |
| **Label manipulation** | Malicious Actor | Modifies CSV labels before training. | MLflow/MinIO | Model learns incorrect associations. | SHA256 hashing of trusted datasets. | Verify hashes before training. |
| **Model artifact tampering**| Insider | Replaces `.pth` file in MinIO. | ML Inference | Inference worker loads backdoor model. | MLflow enforces immutable model versions. | Auditor reviews MLflow logs. |
| **Model replacement** | Insider | Updates MLflow API to point to bad model. | ML Inference | System uses compromised model. | RBAC on MLflow transition actions. | Manager reviews deployment. |
| **Adversarial inputs** | Attacker | Crafts packets to evade feature thresholds. | ML Inference | Attack bypasses ML detection. | Ensemble with deterministic Sigma rules. | Analyst reviews raw logs. |
| **Evasion attacks** | Attacker | Adds noise to payloads (e.g., padding). | ML Inference | Anomaly score drops below threshold. | Robust feature engineering (e.g., entropy). | Rely on correlation of multiple alerts. |
| **Model extraction** | Attacker | Queries API repeatedly to steal weights. | ML Inference | Attacker replicates model locally. | Rate limiting on ingestion API. | N/A (Model is open source for MVP). |
| **Membership inference** | Attacker | Queries to determine if their IP was in training data. | ML Inference | Privacy loss. | Do not use real PII in training sets. | N/A |
| **Excessive false positives**| Model Drift | Normal behavior changes over time. | Incident Worker | Alert fatigue for Analysts. | Dynamic thresholding; analyst feedback loop. | Analyst dismisses alerts. |
| **Excessive false negatives**| Model Bias | Model ignores rare attack vectors. | Incident Worker | Breaches go undetected. | Sigma rules act as safety net. | Penetration testing. |
| **Model drift** | Environment | Network topology changes. | ML Inference | Degraded accuracy. | Track inference metrics in MLflow. | Scheduled model retraining. |
| **Threshold manipulation** | Admin (Compromised) | Raises anomaly threshold to 99%. | Detection Engine | ML alerts never fire. | Audit logs track threshold changes. | Review audit logs. |
| **Prompt injection (logs)** | Attacker | Syslog contains `IGNORE PREVIOUS INSTRUCTIONS`. | Local LLM | AI generates incorrect summary or recommends bad action. | Strip control characters; wrap logs in strict delimiters. | Analyst validates AI output. |
| **Prompt injection (RAG)** | Attacker | Threat intel feed contains malicious prompt. | RAG Knowledge Base | AI acts on malicious instructions. | Treat RAG output as untrusted string literal. | Analyst reviews citations. |
| **Indirect prompt injection**| Attacker | Username in log is malicious prompt. | Local LLM | LLM is hijacked during summarization. | PII masking replaces usernames with safe hashes. | Analyst review. |
| **Sensitive-data disclosure**| Agent Workflow | LLM outputs plaintext passwords found in logs. | Incident UI | PII leaked to analysts unauthorized to see it. | PII masking during normalization. | N/A |
| **Hallucinated evidence** | LLM | LLM makes up an IP address in summary. | Incident UI | Analyst wastes time investigating fake IP. | Prompt requires citing specific Log IDs. | Analyst cross-checks Log ID. |
| **Unsupported conclusions** | LLM | Claims attack is state-sponsored without proof. | Incident UI | Misleading incident reports. | Prompt constrains LLM to factual statements only. | Analyst edits summary. |
| **Tool misuse** | Agent | Agent calls OpenSearch with bad syntax repeatedly. | Agent Workflow | Infinite loop; wasted resources. | LangGraph catches tool errors and forces exit. | N/A |
| **Excessive agency** | Agent | Agent attempts to call `block_ip` directly. | Agent Workflow | Disruption of service. | `block_ip` tool is NOT provided to the Agent. | Architectural hard limit. |
| **Recursive execution** | Agent | Agent calls itself. | Agent Workflow | Compute exhaustion. | `recursion_limit` enforced by LangGraph. | Manual task cancellation. |
| **Denial of wallet (Compute)**| Attacker | Floods system with alerts triggering AI. | Local LLM | GPU/CPU maxed out, system unresponsive. | AI investigation only triggers on High severity. | Manager adjusts auto-trigger logic. |
| **RAG index poisoning** | Attacker | Floods OpenSearch with fake logs to alter RAG. | OpenSearch | Agent retrieves bad context. | Correlation engine groups fake logs separately. | Analyst dismisses fake incident. |
| **Malicious threat-intel** | 3rd Party | API returns fake IoCs. | Processing Worker | Legitimate IPs flagged as malicious. | Validate Threat Intel feeds; use multiple sources. | Analyst overrides alert. |
| **Unsafe response recs.** | LLM | Recommends formatting the database. | Incident UI | Catastrophic failure if approved. | Output constrained against an allowed Playbook list. | Analyst clicks Reject. |
| **Approval bypass** | Attacker | Sends raw POST request to Response Worker. | Response Worker | Unapproved execution. | Worker verifies cryptographic approval in DB. | N/A |
| **Agent audit tampering** | LLM (Compromised) | Agent tries to delete its own reasoning trace. | Postgres | Loss of explainability. | Agent has read-only DB access except for specific tables. | N/A |
