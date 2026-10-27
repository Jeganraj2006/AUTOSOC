from typing import Any, List, Optional, Literal
import uuid
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from autosoc_api.db.session import get_db_session
from autosoc_api.auth.dependencies import require_permission
from autosoc_api.auth.permissions import Permissions
from autosoc_api.auth.models import Principal
from autosoc_api.db.models.response import ResponseRecommendation, ResponseApproval, ResponseExecution
from autosoc_api.db.models.audit_log import AuditLog
from autosoc_api.schemas.response import (
    ResponseRecommendationCreate, ResponseRecommendationResponse,
    ResponseApprovalRequest, ResponseApprovalResponse, ResponseApprovalAction,
    ResponseExecutionCreate, ResponseExecutionResponse
)
from autosoc_api.schemas.search import GlobalResponsePage, GlobalResponseRead, PageMetadata

router = APIRouter()
logger = logging.getLogger(__name__)

_TERMINAL_EXECUTION_STATUSES = {"succeeded", "failed", "timed_out", "cancelled", "rolled_back", "blocked"}
_GLOBAL_RESPONSE_SORT_FIELDS = {
    "created_at": ResponseRecommendation.created_at,
    "status": ResponseRecommendation.status,
    "priority": ResponseRecommendation.priority,
}


def approval_is_expired(expiration: datetime | None, now: datetime | None = None) -> bool:
    """Compare approval expirations as UTC-aware values.

    Older records may contain a naive timestamp, while PostgreSQL returns
    TIMESTAMP WITH TIME ZONE columns as aware timestamps.  Normalising the
    legacy value here keeps the authorization decision deterministic and
    prevents a TypeError from aborting the execution transaction.
    """
    if expiration is None:
        return False
    if expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)
    comparison_time = now or datetime.now(timezone.utc)
    if comparison_time.tzinfo is None:
        comparison_time = comparison_time.replace(tzinfo=timezone.utc)
    return expiration < comparison_time


def add_audit_entry(
    db: AsyncSession,
    principal: Principal,
    action: str,
    target_type: str,
    target_id: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Append an auditable record in the same transaction as a response action."""
    db.add(
        AuditLog(
            id=uuid.uuid4(),
            actor_id=principal.subject_id,
            actor_name=principal.username,
            actor_roles=",".join(principal.roles),
            action=action,
            target_type=target_type,
            target_id=target_id,
            status="success",
            metadata_json=metadata,
        )
    )


def _response_read_options() -> tuple[Any, ...]:
    return (
        selectinload(ResponseRecommendation.approvals),
        selectinload(ResponseRecommendation.executions),
    )


@router.get("/responses", response_model=GlobalResponsePage)
async def list_global_responses(
    status_filter: Optional[str] = None,
    incident_id: Optional[uuid.UUID] = None,
    creator: Optional[str] = None,
    approval_status: Optional[Literal["pending", "approved", "rejected", "expired", "cancelled"]] = None,
    sort_field: Literal["created_at", "status", "priority"] = "created_at",
    sort_direction: Literal["asc", "desc"] = "desc",
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.RESPONSES_READ)),
) -> GlobalResponsePage:
    """List persisted response proposals without replacing incident-scoped reads."""
    if not 1 <= limit <= 250 or not 0 <= offset <= 100_000:
        raise HTTPException(status_code=422, detail="Invalid pagination parameters")
    privileged_roles = {"administrator", "security_manager", "superuser"}
    if creator and creator != current_user.username and not privileged_roles.intersection(current_user.roles):
        raise HTTPException(status_code=403, detail="Creator filtering is limited to your own proposals")

    filters = []
    if status_filter:
        filters.append(ResponseRecommendation.status == status_filter)
    if incident_id:
        filters.append(ResponseRecommendation.incident_id == incident_id)
    if creator:
        filters.append(ResponseRecommendation.created_by == creator)
    if approval_status:
        filters.append(ResponseRecommendation.approvals.any(ResponseApproval.decision == approval_status))

    sort_column = _GLOBAL_RESPONSE_SORT_FIELDS[sort_field]
    primary_sort = asc(sort_column) if sort_direction == "asc" else desc(sort_column)
    tie_breaker = asc(ResponseRecommendation.id) if sort_direction == "asc" else desc(ResponseRecommendation.id)
    statement = (
        select(ResponseRecommendation)
        .where(*filters)
        .options(*_response_read_options())
        .order_by(primary_sort, tie_breaker)
        .limit(limit)
        .offset(offset)
    )
    count_statement = select(func.count()).select_from(ResponseRecommendation).where(*filters)
    total_result, proposals_result = await db.execute(count_statement), await db.execute(statement)
    total = total_result.scalar_one()
    return GlobalResponsePage(
        proposals=[GlobalResponseRead.model_validate(proposal) for proposal in proposals_result.scalars().all()],
        page=PageMetadata(total=total, limit=limit, offset=offset),
    )


@router.get("/responses/{recommendation_id}", response_model=GlobalResponseRead)
async def get_global_response(
    recommendation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.RESPONSES_READ)),
) -> GlobalResponseRead:
    result = await db.execute(
        select(ResponseRecommendation)
        .where(ResponseRecommendation.id == recommendation_id)
        .options(*_response_read_options())
    )
    recommendation = result.scalar_one_or_none()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return GlobalResponseRead.model_validate(recommendation)

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
    await db.flush()
    add_audit_entry(
        db, current_user, "response.recommendation_created", "response_recommendation",
        str(recommendation.id), {"incident_id": str(incident_id), "playbook_id": recommendation.playbook_id},
    )
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
    await db.flush()
    add_audit_entry(
        db, current_user, "response.approval_requested", "response_recommendation",
        str(recommendation_id), {"approval_id": str(approval.id)},
    )
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
        
    # PostgreSQL TIMESTAMP WITH TIME ZONE values are returned as aware UTC
    # datetimes.  Keep application-generated values aware as well so approval
    # expiry checks cannot raise before the execution transaction begins.
    now_utc = datetime.now(timezone.utc)
    approval.decision = action.decision
    approval.reviewer = current_user.username
    approval.decision_at = now_utc
    approval.reason = action.reason
    
    if action.decision == "approved":
        recommendation.status = "approved"
        approval.expiration = now_utc + timedelta(minutes=60)
    else:
        recommendation.status = "rejected"
        
    add_audit_entry(
        db, current_user, f"response.approval_{action.decision}", "response_recommendation",
        str(recommendation_id), {"approval_id": str(approval.id), "reason": action.reason},
    )
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
    if str(recommendation_id) != str(execution_in.recommendation_id):
        raise HTTPException(status_code=400, detail="Recommendation ID mismatch")

    rec_result = await db.execute(
        select(ResponseRecommendation).where(ResponseRecommendation.id == recommendation_id)
    )
    recommendation = rec_result.scalars().first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    idempotency_key = f"{recommendation_id}_{execution_in.mode}"

    # Look up a completed execution before validating the mutable proposal
    # state.  A successful dry run changes the recommendation to ``executed``;
    # retries with the same key must return that completed record rather than
    # being rejected as no longer ``approved``.
    ex_result = await db.execute(
        select(ResponseExecution)
        .where(ResponseExecution.idempotency_key == idempotency_key)
        .with_for_update()
    )
    existing = ex_result.scalars().first()
    if existing and existing.status in _TERMINAL_EXECUTION_STATUSES:
        logger.info(
            "response execution idempotency hit: recommendation_id=%s mode=%s execution_id=%s status=%s",
            recommendation_id,
            execution_in.mode,
            existing.id,
            existing.status,
        )
        return existing

    approval = None
    if recommendation.approval_required:
        if recommendation.status != "approved":
            raise HTTPException(status_code=400, detail="Execution requires an approved recommendation")

        app_result = await db.execute(
            select(ResponseApproval).where(
                ResponseApproval.recommendation_id == recommendation_id,
                ResponseApproval.decision == "approved"
            )
        )
        approval = app_result.scalars().first()
        now_utc = datetime.now(timezone.utc)
        if not approval or approval_is_expired(approval.expiration, now_utc):
            raise HTTPException(status_code=400, detail="Valid unexpired approval required for execution")

    if existing:
        execution = existing
        logger.warning(
            "recovering non-terminal response execution: recommendation_id=%s mode=%s execution_id=%s status=%s",
            recommendation_id,
            execution_in.mode,
            execution.id,
            execution.status,
        )
    else:
        execution = ResponseExecution(
            recommendation_id=recommendation.id,
            approval_id=approval.id if approval else None,
            playbook_id=recommendation.playbook_id,
            action_type=recommendation.action_type,
            mode=execution_in.mode,
            target=recommendation.target_reference,
            executor="dry_run_validator" if execution_in.mode == "dry_run" else "pending",
            idempotency_key=idempotency_key,
        )
        db.add(execution)
        try:
            await db.flush()
        except IntegrityError:
            # A concurrent request won the unique idempotency-key race.  The
            # unique index makes this retry safe; reload the committed winner.
            await db.rollback()
            existing_result = await db.execute(
                select(ResponseExecution)
                .where(ResponseExecution.idempotency_key == idempotency_key)
                .with_for_update()
            )
            execution = existing_result.scalars().one()
            if execution.status in _TERMINAL_EXECUTION_STATUSES:
                return execution

    if execution_in.mode == "dry_run":
        now_utc = datetime.now(timezone.utc)
        execution.status = "succeeded"
        execution.completed_at = now_utc
        execution.verification_status = "verified"
        execution.result = {
            "dry_run": True,
            "outcome": "validated_only",
            "message": "No external containment action was attempted.",
        }
        recommendation.status = "executed"
    elif existing:
        # Only validated dry runs may be resumed automatically.  Other modes
        # remain queued for their explicit executor and never trigger an
        # external security action from an idempotency retry.
        logger.info(
            "non-dry-run response execution remains queued: recommendation_id=%s execution_id=%s mode=%s",
            recommendation_id,
            execution.id,
            execution_in.mode,
        )
    add_audit_entry(
        db, current_user, "response.execution_requested", "response_execution",
        str(execution.id), {"recommendation_id": str(recommendation_id), "mode": execution_in.mode},
    )
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
    add_audit_entry(
        db, current_user, "response.rollback_requested", "response_execution", str(execution.id)
    )
    await db.commit()
    return {"message": "Rollback initiated"}
