from typing import Any, List
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from autosoc_api.db.session import get_db_session
from autosoc_api.auth.dependencies import require_permission
from autosoc_api.auth.permissions import Permissions
from autosoc_api.auth.models import Principal
from autosoc_api.db.models.response import ResponseRecommendation, ResponseApproval, ResponseExecution
from autosoc_api.schemas.response import (
    ResponseRecommendationCreate, ResponseRecommendationResponse,
    ResponseApprovalRequest, ResponseApprovalResponse, ResponseApprovalAction,
    ResponseExecutionCreate, ResponseExecutionResponse
)

router = APIRouter()

@router.post("/incidents/{incident_id}/responses", response_model=ResponseRecommendationResponse)
async def create_recommendation(
    incident_id: uuid.UUID,
    recommendation_in: ResponseRecommendationCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.RESPONSES_RECOMMEND))
) -> Any:
    """
    Create a new response recommendation.
    """
    if str(incident_id) != str(recommendation_in.incident_id):
        raise HTTPException(status_code=400, detail="Incident ID mismatch")
    
    recommendation = ResponseRecommendation(
        **recommendation_in.model_dump(),
        created_by=current_user.username
    )
    db.add(recommendation)
    await db.commit()
    await db.refresh(recommendation)
    return recommendation

@router.get("/incidents/{incident_id}/responses", response_model=List[ResponseRecommendationResponse])
async def list_recommendations(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.RESPONSES_READ))
) -> Any:
    """
    List response recommendations for an incident.
    """
    result = await db.execute(
        select(ResponseRecommendation).where(ResponseRecommendation.incident_id == incident_id)
    )
    return result.scalars().all()

@router.post("/responses/{recommendation_id}/request-approval", response_model=ResponseApprovalResponse)
async def request_approval(
    recommendation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.RESPONSES_RECOMMEND))
) -> Any:
    """
    Request approval for a proposed recommendation.
    """
    result = await db.execute(
        select(ResponseRecommendation).where(ResponseRecommendation.id == recommendation_id)
    )
    recommendation = result.scalars().first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    if recommendation.status != "proposed":
        raise HTTPException(status_code=400, detail="Recommendation is not in proposed state")
        
    recommendation.status = "pending_review"
    
    approval = ResponseApproval(
        recommendation_id=recommendation.id,
        incident_id=recommendation.incident_id,
        requested_by=current_user.username
    )
    db.add(approval)
    await db.commit()
    await db.refresh(approval)
    return approval

@router.post("/responses/{recommendation_id}/approve", response_model=ResponseApprovalResponse)
async def approve_recommendation(
    recommendation_id: uuid.UUID,
    action: ResponseApprovalAction,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.RESPONSES_APPROVE))
) -> Any:
    """
    Approve or reject a recommendation.
    """
    rec_result = await db.execute(
        select(ResponseRecommendation).where(ResponseRecommendation.id == recommendation_id)
    )
    recommendation = rec_result.scalars().first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if recommendation.created_by == current_user.username:
        raise HTTPException(status_code=403, detail="A recommendation cannot be approved by its author")
        
    app_result = await db.execute(
        select(ResponseApproval).where(
            ResponseApproval.recommendation_id == recommendation_id,
            ResponseApproval.decision == "pending"
        )
    )
    approval = app_result.scalars().first()
    
    if not approval:
        raise HTTPException(status_code=400, detail="No pending approval request found")
        
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    approval.decision = action.decision
    approval.reviewer = current_user.username
    approval.decision_at = now_utc
    approval.reason = action.reason
    
    if action.decision == "approved":
        recommendation.status = "approved"
        approval.expiration = now_utc + timedelta(minutes=60)
    else:
        recommendation.status = "rejected"
        
    await db.commit()
    await db.refresh(approval)
    return approval

@router.post("/responses/{recommendation_id}/execute", response_model=ResponseExecutionResponse)
async def execute_recommendation(
    recommendation_id: uuid.UUID,
    execution_in: ResponseExecutionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.RESPONSES_EXECUTE))
) -> Any:
    """
    Execute a response (dry-run, simulation, analyst_approved_execution).
    """
    rec_result = await db.execute(
        select(ResponseRecommendation).where(ResponseRecommendation.id == recommendation_id)
    )
    recommendation = rec_result.scalars().first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    approval = None
    if execution_in.mode == "analyst_approved_execution":
        if recommendation.status != "approved":
            raise HTTPException(status_code=400, detail="Execution requires an approved recommendation")
            
        app_result = await db.execute(
            select(ResponseApproval).where(
                ResponseApproval.recommendation_id == recommendation_id,
                ResponseApproval.decision == "approved"
            )
        )
        approval = app_result.scalars().first()
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        if not approval or (approval.expiration and approval.expiration < now_utc):
            raise HTTPException(status_code=400, detail="Valid unexpired approval required for execution")
    
    idempotency_key = f"{recommendation_id}_{execution_in.mode}"
    
    ex_result = await db.execute(
        select(ResponseExecution).where(ResponseExecution.idempotency_key == idempotency_key)
    )
    existing = ex_result.scalars().first()
    if existing:
        return existing
        
    execution = ResponseExecution(
        recommendation_id=recommendation.id,
        approval_id=approval.id if approval else None,
        playbook_id=recommendation.playbook_id,
        action_type=recommendation.action_type,
        mode=execution_in.mode,
        target=recommendation.target_reference,
        executor="pending",
        idempotency_key=idempotency_key
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    return execution

@router.post("/response-executions/{execution_id}/rollback")
async def rollback_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.RESPONSES_MANAGE))
) -> Any:
    """
    Request rollback of a completed execution.
    """
    result = await db.execute(
        select(ResponseExecution).where(ResponseExecution.id == execution_id)
    )
    execution = result.scalars().first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
        
    if execution.status not in ["succeeded", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot rollback execution in current state")
        
    execution.status = "rollback_pending"
    await db.commit()
    return {"message": "Rollback initiated"}
