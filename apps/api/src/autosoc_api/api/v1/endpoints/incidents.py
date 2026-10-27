from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from autosoc_api.db.session import get_db_session
from autosoc_api.schemas.incident import IncidentResponse, IncidentUpdate, IncidentNoteResponse, IncidentNoteCreate
from autosoc_api.services.incident import IncidentService
from autosoc_api.services.incident_transition import IncidentTransitionService
from autosoc_api.db.models.incident import IncidentStatus
from autosoc_api.auth.dependencies import require_permission
from autosoc_api.auth.models import Principal
from autosoc_api.auth.permissions import Permissions

router = APIRouter()

@router.get("/", response_model=List[IncidentResponse])
async def list_incidents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.INCIDENTS_READ)),
):
    service = IncidentService(db)
    return await service.get_all(skip=skip, limit=limit)

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.INCIDENTS_READ)),
):
    service = IncidentService(db)
    return await service.get_by_id(incident_id)

@router.patch("/{incident_id}/status", response_model=IncidentResponse)
async def update_status(
    incident_id: uuid.UUID, 
    status: IncidentStatus, 
    reason: str = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.INCIDENTS_UPDATE)),
):
    service = IncidentTransitionService(db)
    return await service.update_status(incident_id, status, current_user.subject_id, reason)

from autosoc_api.db.models.alert import Alert
from autosoc_api.db.models.incident_alert import IncidentAlert
from autosoc_api.schemas.alert import AlertResponse
from sqlalchemy import select

@router.get("/{incident_id}/alerts", response_model=List[AlertResponse])
async def get_incident_alerts(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.INCIDENTS_READ)),
):
    # Alerts can contribute evidence to more than one correlation.  The
    # legacy Alert.incident_id field holds only one of those associations, so
    # use the durable link table rather than silently dropping linked alerts.
    stmt = (
        select(Alert)
        .join(IncidentAlert, IncidentAlert.alert_id == Alert.id)
        .where(IncidentAlert.incident_id == incident_id)
        .order_by(IncidentAlert.linked_at.asc(), Alert.id.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{incident_id}/notes", response_model=List[IncidentNoteResponse])
async def get_notes(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.INCIDENTS_READ)),
):
    service = IncidentService(db)
    return await service.get_notes(incident_id)

@router.post("/{incident_id}/notes", response_model=IncidentNoteResponse)
async def create_note(
    incident_id: uuid.UUID,
    note: IncidentNoteCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.INCIDENTS_UPDATE)),
):
    service = IncidentService(db)
    return await service.create_note(incident_id, note, current_user.subject_id)
