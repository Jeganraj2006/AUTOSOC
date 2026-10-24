# ADR-013: Separate Detection and LLM Responsibilities

## Status
Accepted

## Context
Large Language Models (LLMs) are powerful but prone to hallucination, non-determinism, and slow execution. Relying on an LLM to evaluate millions of incoming logs for threats is computationally unfeasible and unsafe.

## Decision
We strictly separate deterministic/statistical detection from LLM-driven explanation and investigation. 
1. **Detection Engine**: Sigma rules and ML models (PyTorch/scikit-learn) evaluate logs at scale to generate alerts and identify potential zero-days.
2. **LLM/Agent**: Only invoked *after* an alert is generated to summarize findings, query related context (RAG), and recommend responses.

## Alternatives Considered
- **LLM-only Detection**: Rejected due to extreme cost, latency, and hallucination risks.

## Positive Consequences
- System performance remains high (detection is fast).
- Alerts are deterministic and explainable.
- LLM context windows are preserved for analyzing specific, correlated incidents rather than a firehose of raw logs.

## Negative Consequences
- Requires maintaining separate skillsets (Rule creation, ML engineering, Prompt engineering).

## Security Implications
- Prevents the LLM from missing obvious attacks due to context-window truncation.
- Enforces the principle that AI is an analyst-assist tool, not a primary detection mechanism.

## Revisit Conditions
- N/A; This separation is a core tenet of the project's safety architecture.
