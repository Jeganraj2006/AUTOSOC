# ADR-009: LangGraph for Agent Workflows

## Status
Accepted

## Context
AutoSOC requires Agentic AI to investigate incidents, query OpenSearch, and formulate responses. Simple LLM calls (chains) are insufficient for multi-step reasoning, tool use, and stateful interactions (e.g., looping until enough context is gathered).

## Decision
We will use LangGraph to orchestrate Agentic AI workflows. The agent will execute locally using Ollama initially.

## Alternatives Considered
- **LangChain (Standard Agents)**: Rejected because traditional LangChain agents lack explicit graph-based control flow, making them harder to debug, prone to infinite loops, and difficult to pause for human approval.
- **AutoGPT / BabyAGI**: Rejected because they are too unstructured and autonomous, violating our strict safety constraint against unrestricted AI actions.
- **Custom State Machine**: Rejected because building a resilient orchestrator from scratch detracts from focusing on the security use cases.

## Positive Consequences
- Explicit state management and cyclical graph definitions.
- Easy to inject "human-in-the-loop" pauses (e.g., waiting for approval).
- Better observability and debugging of the agent's thought process.

## Negative Consequences
- Steeper learning curve compared to simple prompt chains.
- Requires careful state management to avoid exceeding the LLM context window.

## Security Implications
- LangGraph allows us to strictly define which nodes (tools) the agent can transition to, preventing it from executing unauthorized functions.

## Revisit Conditions
- If LangGraph proves too slow or complex for simple RAG tasks, we may fall back to simpler chains for those specific tasks, reserving LangGraph for full incident investigation.
