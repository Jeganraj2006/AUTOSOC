# AI and ML architecture

Deterministic workers create detections, correlations and predictions. The durable `agent-worker` consumes correlated incidents, retrieves persisted alert evidence, invokes the configured local Ollama model, and saves model metadata, node status, timestamps, retry count, failure data, evidence references, and the raw advisory analysis in `agent_executions`.

Logical workflow nodes include detection verification, investigation, threat-intelligence context, risk assessment, prediction analysis, response recommendation, and reporting. These nodes are not independent AI services. The agent worker is the one active inference consumer. Its prompt explicitly requests evidence-only reasoning and prohibits executable containment instructions; model output cannot create, approve, or execute a response.

The repository also retains an older API background LangGraph path. It is not the verified durable pipeline and should be consolidated with the durable worker before any production assessment. No accuracy, precision, prevention claim, or model confidence score is asserted by this release.
