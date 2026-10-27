from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, func, or_, cast, String
from typing import List, Optional, Literal
from uuid import UUID
from datetime import datetime

from autosoc_api.db.session import get_db_session
from autosoc_api.db.models.alert import Alert
from autosoc_api.schemas.alert import AlertResponse, AlertUpdate
from autosoc_api.schemas.search import AlertSearchResponse, PageMetadata
from autosoc_api.auth.dependencies import require_permission
from autosoc_api.auth.permissions import Permissions
from autosoc_api.auth.models import Principal
from autosoc_api.audit.audit_service import audit_log

router = APIRouter()

_ALERT_SORT_FIELDS = {
    "created_at": Alert.created_at,
    "updated_at": Alert.updated_at,
    "severity": Alert.severity,
    "status": Alert.status,
    "title": Alert.title,
}

import uuid
from datetime import datetime, timezone
from autosoc_api.db.models.incident import Incident

@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    db: AsyncSession = Depends(get_db_session),
    user: Principal = Depends(require_permission(Permissions.ALERTS_READ)),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0
):
    stmt = select(Alert).order_by(desc(Alert.created_at)).limit(limit).offset(offset)
    if status:
        stmt = stmt.where(Alert.status == status)
    if severity:
        stmt = stmt.where(Alert.severity == severity)
        
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    return alerts


@router.get("/search", response_model=AlertSearchResponse)
async def search_alerts(
    db: AsyncSession = Depends(get_db_session),
    user: Principal = Depends(require_permission(Permissions.ALERTS_READ)),
    q: Optional[str] = Query(None, max_length=256, description="Search identifier, title, or description"),
    status: Optional[str] = Query(None, max_length=64),
    severity: Optional[str] = Query(None, max_length=64),
    incident_id: Optional[UUID] = None,
    rule_id: Optional[str] = Query(None, max_length=255),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    sort_field: Literal["created_at", "updated_at", "severity", "status", "title"] = "created_at",
    sort_direction: Literal["asc", "desc"] = "desc",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0, le=100_000),
) -> AlertSearchResponse:
    """Return an authenticated, paged alert read model.

    The legacy ``GET /alerts/`` array response is intentionally preserved for
    consumers that have not moved to an explicit total/pagination contract.
    """
    if start_time and end_time and start_time > end_time:
        raise HTTPException(status_code=422, detail="start_time must be before end_time")

    filters = []
    if q:
        pattern = f"%{q}%"
        filters.append(
            or_(
                cast(Alert.id, String).ilike(pattern),
                Alert.title.ilike(pattern),
                Alert.description.ilike(pattern),
            )
        )
    if status:
        filters.append(Alert.status == status)
    if severity:
        filters.append(Alert.severity == severity)
    if incident_id:
        filters.append(Alert.incident_id == incident_id)
    if rule_id:
        filters.append(Alert.rule_id == rule_id)
    if start_time:
        filters.append(Alert.created_at >= start_time)
    if end_time:
        filters.append(Alert.created_at <= end_time)

    sort_column = _ALERT_SORT_FIELDS[sort_field]
    primary_sort = asc(sort_column) if sort_direction == "asc" else desc(sort_column)
    tie_breaker = asc(Alert.id) if sort_direction == "asc" else desc(Alert.id)
    statement = select(Alert).where(*filters).order_by(primary_sort, tie_breaker).limit(limit).offset(offset)
    count_statement = select(func.count()).select_from(Alert).where(*filters)
    total, result = await db.execute(count_statement), await db.execute(statement)
    count = total.scalar_one()
    return AlertSearchResponse(
        alerts=list(result.scalars().all()),
        page=PageMetadata(total=count, limit=limit, offset=offset),
    )

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    user: Principal = Depends(require_permission(Permissions.ALERTS_READ))
):
    stmt = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.patch("/{alert_id}/status", response_model=AlertResponse)
async def update_alert_status(
    alert_id: UUID,
    update_data: AlertUpdate,
    db: AsyncSession = Depends(get_db_session),
    user: Principal = Depends(require_permission(Permissions.ALERTS_UPDATE))
):
    stmt = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    old_status = alert.status
    if update_data.status:
        alert.status = update_data.status
        
    await db.commit()
    await db.refresh(alert)
    
    await audit_log(
        db,
        user.subject_id,
        "UPDATE_ALERT_STATUS",
        f"Alert {alert_id} status changed from {old_status} to {alert.status}",
        True
    )
    
    return alert
