"""Read-only, role-protected audit history for the operations UI."""

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from autosoc_api.auth.dependencies import require_permission
from autosoc_api.auth.models import Principal
from autosoc_api.auth.permissions import Permissions
from autosoc_api.db.models.audit_log import AuditLog
from autosoc_api.db.session import get_db_session
from autosoc_api.schemas.search import AuditPage, AuditRecordRead, PageMetadata

router = APIRouter()

_SENSITIVE_METADATA_MARKERS = ("password", "secret", "token", "authorization", "cookie", "api_key", "apikey")


def redact_metadata(value: Any) -> Any:
    """Remove secret-bearing values while retaining an honest audit shape."""
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if any(marker in key.lower() for marker in _SENSITIVE_METADATA_MARKERS) else redact_metadata(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_metadata(item) for item in value]
    return value


@router.get("/", response_model=AuditPage)
async def list_audit_records(
    action: str | None = Query(None, max_length=100),
    actor: str | None = Query(None, max_length=255),
    resource_type: str | None = Query(None, max_length=100),
    resource_id: str | None = Query(None, max_length=255),
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    sort_direction: Literal["asc", "desc"] = "desc",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0, le=100_000),
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.AUDIT_READ)),
) -> AuditPage:
    if start_time and end_time and start_time > end_time:
        raise HTTPException(status_code=422, detail="start_time must be before end_time")

    filters = []
    if action:
        filters.append(AuditLog.action == action)
    if actor:
        filters.append(AuditLog.actor_id == actor)
    if resource_type:
        filters.append(AuditLog.target_type == resource_type)
    if resource_id:
        filters.append(AuditLog.target_id == resource_id)
    if start_time:
        filters.append(AuditLog.created_at >= start_time)
    if end_time:
        filters.append(AuditLog.created_at <= end_time)

    timestamp_order = asc(AuditLog.created_at) if sort_direction == "asc" else desc(AuditLog.created_at)
    id_order = asc(AuditLog.id) if sort_direction == "asc" else desc(AuditLog.id)
    statement = select(AuditLog).where(*filters).order_by(timestamp_order, id_order).limit(limit).offset(offset)
    count_statement = select(func.count()).select_from(AuditLog).where(*filters)
    total_result, records_result = await db.execute(count_statement), await db.execute(statement)
    records = []
    for entry in records_result.scalars().all():
        records.append(
            AuditRecordRead(
                id=entry.id,
                timestamp=entry.created_at,
                actor_id=entry.actor_id,
                actor_name=entry.actor_name,
                action=entry.action,
                resource_type=entry.target_type,
                resource_id=entry.target_id,
                result=entry.status,
                correlation_id=entry.request_id,
                metadata=redact_metadata(entry.metadata_json),
            )
        )
    return AuditPage(
        records=records,
        page=PageMetadata(total=total_result.scalar_one(), limit=limit, offset=offset),
    )
