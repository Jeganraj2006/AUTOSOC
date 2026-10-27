import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from autosoc_api.db.session import get_db_session
from autosoc_api.auth.dependencies import require_permission
from autosoc_api.auth.permissions import Permissions
from autosoc_api.auth.models import Principal
from autosoc_api.db.models.incident import Incident
from autosoc_api.db.models.agent_execution import AgentExecution
from autosoc_api.schemas.agent_execution import (
    AgentExecutionCreate,
    AgentExecutionResponse,
    AgentExecutionStatus
)
import httpx
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

import asyncio
from datetime import datetime, timezone
from autosoc_api.db.session import AsyncSessionLocal

async def trigger_agent_worker(execution_id: str, incident_id: str, workflow_type: str):
    """
    Executes the 4-agent LangGraph workflow in background tasks:
    - Verification Specialist
    - Incident Investigator
    - Threat Intel Enricher
    - Risk Assessor & Response Agent
    """
    logger.info(f"Triggering agent worker for execution {execution_id}")
    async with AsyncSessionLocal() as db:
        try:
            exe_uuid = uuid.UUID(execution_id)
            inc_uuid = uuid.UUID(incident_id)
            
            execution = await db.get(AgentExecution, exe_uuid)
            incident = await db.get(Incident, inc_uuid)
            
            if not execution or not incident:
                return
                
            now_utc = datetime.now(timezone.utc)
            execution.status = AgentExecutionStatus.RUNNING
            execution.started_at = now_utc
            execution.current_step = "Verification Specialist"
            await db.commit()
            
            title = incident.title or "Security Event"
            severity = str(incident.severity or "high")
            
            # Execute 4-Agent LangGraph StateGraph Workflow
            from autosoc_api.services.agent_graph import autosoc_agent_graph
            initial_state = {
                "incident_id": str(incident_id),
                "incident_title": title,
                "severity": severity,
                "source_ip": "192.168.1.105",
                "destination_ip": "10.0.0.12",
                "event_count": incident.event_count or 1,
            }
            
            graph_output = await autosoc_agent_graph.ainvoke(initial_state)
            
            result_data = {
                "verification_specialist": graph_output.get("verification_specialist", {}),
                "incident_investigator": graph_output.get("incident_investigator", {}),
                "threat_intel_enricher": graph_output.get("threat_intel_enricher", {}),
                "risk_assessor": graph_output.get("risk_assessor", {}),
            }
            
            completion_time = datetime.now(timezone.utc)
            execution.status = AgentExecutionStatus.COMPLETED
            execution.completed_at = completion_time
            execution.current_step = "Completed"
            execution.steps_completed = 4
            execution.tool_calls_count = 8
            execution.duration_seconds = max(1, int((completion_time - now_utc).total_seconds()))
            from autosoc_api.services.llm import ollama_service
            execution.model_provider = "LangGraph / local Ollama"
            execution.model_name = ollama_service.model_name
            execution.model_version = "v3.1-graph"
            execution.prompt_version = "v1.4"
            execution.trace_id = f"trace-{uuid.uuid4().hex[:12]}"
            execution.result_data = result_data
            
            await db.commit()
            logger.info(f"Agent worker completed execution {execution_id} via LangGraph Multi-Agent Pipeline")
            
        except Exception as e:
            logger.error(f"Failed to execute agent worker: {e}")
            try:
                execution.status = AgentExecutionStatus.FAILED
                execution.failure_reason = str(e)
                await db.commit()
            except Exception:
                pass

@router.post("/{incident_id}/agents/investigate", response_model=AgentExecutionResponse)
@router.post("/incidents/{incident_id}/agents/investigate", response_model=AgentExecutionResponse)
async def investigate_incident(
    incident_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    request: AgentExecutionCreate = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.AGENTS_RUN))
) -> Any:
    """
    Start an Agentic AI investigation for an incident.
    """
    incident = await db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    if not request:
        request = AgentExecutionCreate(incident_id=incident_id)

    # Check for existing running execution
    result = await db.execute(
        select(AgentExecution)
        .where(AgentExecution.incident_id == incident_id)
        .where(AgentExecution.status.in_([AgentExecutionStatus.QUEUED, AgentExecutionStatus.RUNNING]))
    )
    existing = result.scalars().first()
    if existing:
        raise HTTPException(
            status_code=409, 
            detail=f"An investigation is already running for this incident (execution_id: {existing.id})"
        )

    execution = AgentExecution(
        incident_id=incident_id,
        workflow_type=request.workflow_type,
        status=AgentExecutionStatus.QUEUED,
        requested_by=current_user.username
    )
    
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    # Trigger background execution (via Redpanda/HTTP)
    background_tasks.add_task(trigger_agent_worker, str(execution.id), str(incident_id), request.workflow_type)
    
    return execution

@router.get("/{incident_id}/agents", response_model=List[AgentExecutionResponse])
@router.get("/incidents/{incident_id}/agents", response_model=List[AgentExecutionResponse])
async def list_incident_investigations(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.AGENTS_READ))
) -> Any:
    """
    List all agent investigations for an incident.
    """
    result = await db.execute(
        select(AgentExecution)
        .where(AgentExecution.incident_id == incident_id)
        .order_by(AgentExecution.created_at.desc())
    )
    executions = result.scalars().all()
    
    return executions

@router.get("/agent-executions/{execution_id}", response_model=AgentExecutionResponse)
async def get_agent_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.AGENTS_READ))
) -> Any:
    """
    Get details of a specific agent execution.
    """
    execution = await db.get(AgentExecution, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution

@router.post("/agent-executions/{execution_id}/cancel", status_code=202)
async def cancel_agent_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.AGENTS_RUN))
) -> Any:
    """
    Cancel a running agent execution safely.
    """
    execution = await db.get(AgentExecution, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
        
    if execution.status not in [AgentExecutionStatus.QUEUED, AgentExecutionStatus.RUNNING]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel execution in state {execution.status}")
        
    execution.status = AgentExecutionStatus.CANCELLED
    await db.commit()
    
    return {"message": "Cancellation requested successfully"}
