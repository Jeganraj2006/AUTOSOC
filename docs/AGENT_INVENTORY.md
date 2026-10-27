# Agent inventory

The repository contains eleven logical graph nodes: four API graph nodes (`verification`, `investigator`, `threat_intel`, `risk_assessor`) and seven worker graph nodes (`detection_verification`, `investigation`, `threat_intelligence`, `risk_assessment`, `prediction_analysis`, `response_recommendation`, `reporting`).

The agent worker now consumes `security.incidents` as `autosoc-agent-worker-group`, retrieves persisted incident/alert evidence, invokes the local `llama3.2:3b` Ollama endpoint with a bounded evidence-only prompt, and writes an `agent_executions` record. One complete message-to-database investigation was verified with an Ollama HTTP 200 response. This is one verified end-to-end AI path, not verification of all eleven logical nodes: the API graph's first three nodes and the worker graph's seven legacy nodes still contain procedural/static behavior and must not be represented as independent AI investigations.

High-impact recommendations remain approval-gated. No real response action was executed during validation.
