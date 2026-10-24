# Project Glossary and Terminology

To maintain academic rigor and avoid sensationalist claims, AutoSOC enforces strict terminology, particularly regarding the identification of "zero-day" threats. The system cannot definitively prove a zero-day vulnerability; it can only flag statistical deviations and unrecognized patterns.

## AutoSOC Specific Terminology

- **Suspicious Anomaly**: A sequence of events or metric that deviates significantly from the established baseline of normal network behavior, requiring investigation.
- **Previously Unseen Behaviour**: Network traffic or system activity that does not match historical training data or existing deterministic rules.
- **Potential Zero-Day Behaviour**: A highly suspicious anomaly, classified with high confidence by the ML model, that exhibits characteristics of an attack but lacks a known signature. *This is the highest severity system-generated classification before human review.*
- **High-Risk Unknown Activity**: Activity that touches critical assets and deviates from the baseline, but does not strictly map to known malicious patterns.
- **Known Attack**: Malicious activity that triggers a deterministic, signature-based rule (e.g., a Sigma rule match for a known Mimikatz execution).
- **Benign Activity**: Normal, expected system or network behavior that poses no threat.

## General Cybersecurity Terminology

- **Zero-Day Vulnerability**: A software flaw unknown to the vendor and without a patch available.
- **Zero-Day Exploit**: A cyberattack that utilizes a zero-day vulnerability.
- **Previously Unseen Attack Pattern**: A novel sequence of tactics and techniques used by an attacker, which may utilize known tools in new ways, or exploit unknown vulnerabilities.
- **Anomaly**: Any data point or sequence that deviates from expected behavior. Not all anomalies are security threats (e.g., a sudden spike in legitimate web traffic).
- **Confirmed Security Incident**: An event or series of events that has been reviewed by a human SOC Analyst and verified to be a breach or attempted breach of security policies.

## Terminology Rule Enforcement
- The UI and LLM prompts must **never** state: *"This is a zero-day attack."*
- The UI and LLM prompts **must** state: *"This exhibits potential zero-day behaviour."* or *"This anomaly has a 95% confidence score of being malicious."*

## Architecture and Infrastructure Terminology
- **Modular Monolith**: An architecture where code is separated into strictly defined modules (e.g., in FastAPI) rather than distributed across many separate microservices, balancing organization with deployment simplicity.
- **Background Worker**: An independent process consuming tasks from a message broker (Redpanda) to perform heavy computing asynchronously without blocking the main API.
- **Retrieval-Augmented Generation (RAG)**: The process of querying a database (OpenSearch) for relevant context and injecting it into the LLM prompt to ground the AI's conclusions in factual data.
- **Dead-Letter Queue (DLQ)**: A storage destination (e.g., a specific Redpanda topic) for events that fail processing or validation, preventing silent data loss and allowing for later analysis.
- **Idempotency**: The property of a process (like a playbook execution or DB write) that guarantees applying it multiple times yields the same result as applying it once.
