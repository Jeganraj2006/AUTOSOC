# Phase 15: Agentic AI Investigation and RAG - Implementation Plan

## Goal Description
Implement an Agentic AI workflow using LangGraph to automate the investigation, evidence collection, threat context retrieval (via RAG), risk assessment, prediction analysis, and response recommendation for SOC incidents. The workflow will use a local LLM (Ollama) and OpenSearch for vector-based RAG. The workflow will strictly enforce AI-safety limits: no autonomous response execution, no arbitrary internet access, and no overriding of deterministic backend data.

## User Review Required

> [!IMPORTANT]
> The orchestrator will be built using LangGraph, and Ollama will be used as the local LLM as defined by ADR-009. We will use OpenSearch for RAG Vector Storage as defined by ADR-014. Please confirm that these tool choices and boundary constraints align with your current hardware setup and security goals.

## Open Questions
1. **Ollama Model**: Do you have a specific Ollama model already downloaded and preferred for this phase (e.g., `llama3.1`, `mistral`)? We will configure the application to use it.
2. **OpenSearch Indexing**: Should we create a new distinct OpenSearch index for RAG knowledge chunks, or namespace it within an existing index? A dedicated `autosoc-knowledge` index is proposed.

## Proposed Changes

---

### Backend API and Database Models (Core)

#### [MODIFY] [incident.py](file:///d:/PROJECT%20WORKKKKKKKKKK/apps/api/src/autosoc_api/db/models/incident.py)
- Extend or create the `AgentExecution` model linked to an `Incident` to track the state, model used, duration, and final results of an agent investigation. 

#### [NEW] [agent_execution.py](file:///d:/PROJECT%20WORKKKKKKKKKK/apps/api/src/autosoc_api/schemas/agent_execution.py)
- Pydantic schemas for Agent Execution state, requests, and responses.

#### [NEW] [agents.py](file:///d:/PROJECT%20WORKKKKKKKKKK/apps/api/src/autosoc_api/api/v1/endpoints/agents.py)
- API router exposing `POST /api/v1/incidents/{incident_id}/agents/investigate` and `GET /api/v1/incidents/{incident_id}/agents`.

---

### Agent Worker Module

#### [NEW] [workers/agents/pyproject.toml](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/agents/pyproject.toml)
- Define the new microservice for agents.
- Dependencies: `langgraph`, `langchain-community`, `langchain-core`, `pydantic`, `opensearch-py`, etc.

#### [NEW] [workers/agents/src/autosoc_agents/orchestrator/graph.py](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/agents/src/autosoc_agents/orchestrator/graph.py)
- The core LangGraph state machine definition, compiling the nodes (agents) and conditional edges.

#### [NEW] [workers/agents/src/autosoc_agents/agents/*.py](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/agents/src/autosoc_agents/agents/)
- Implement specialized nodes:
  - `detection_verification.py`
  - `investigation.py`
  - `threat_intelligence.py`
  - `risk_assessment.py`
  - `prediction_analysis.py`
  - `response_recommendation.py`
  - `reporting.py`

#### [NEW] [workers/agents/src/autosoc_agents/tools/](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/agents/src/autosoc_agents/tools/)
- Allowlisted tools (e.g., `get_incident`, `get_alert`, `search_knowledge`).

#### [NEW] [workers/agents/src/autosoc_agents/prompts/](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/agents/src/autosoc_agents/prompts/)
- Versioned system prompts with strict injection guardrails.

#### [NEW] [workers/agents/src/autosoc_agents/rag/](file:///d:/PROJECT%20WORKKKKKKKKKK/workers/agents/src/autosoc_agents/rag/)
- Document ingestion, chunking, OpenSearch vector retrieval logic.

---

### Frontend UI

#### [MODIFY] [page.tsx](file:///d:/PROJECT%20WORKKKKKKKKKK/apps/web/src/app/(soc)/incidents/[id]/page.tsx)
- Add a new "AI Investigation" tab.
- Add "Run AI Investigation" button.

#### [NEW] [agent-investigation-panel.tsx](file:///d:/PROJECT%20WORKKKKKKKKKK/apps/web/src/components/incidents/agent-investigation-panel.tsx)
- Display execution progress, structured findings, risk, recommendations, and evidence citations.

---

### Documentation & Configurations

#### [NEW] [docs/186-phase-15-implementation-plan.md](file:///d:/PROJECT%20WORKKKKKKKKKK/docs/186-phase-15-implementation-plan.md)
- Mirror of this plan in the repo.

#### [MODIFY] [docker/compose.yml](file:///d:/PROJECT%20WORKKKKKKKKKK/infrastructure/docker/compose.yml)
- Add `agent-worker` service to the docker-compose stack.

## Verification Plan

### Automated Tests
- `pytest` for the `autosoc_agents` worker module, using a mock LLM adapter to verify LangGraph execution flow, tool permissions, and structured output parsing.
- E2E API tests in `apps/api` for the execution endpoints.
- RAG poisoning and prompt-injection tests.

### Manual Verification
- Trigger an AI investigation from the UI on an existing incident.
- Verify that the frontend displays the structured report with valid citations.
- Check the backend logs to ensure no out-of-bounds tools were called and Ollama inference completed successfully.
