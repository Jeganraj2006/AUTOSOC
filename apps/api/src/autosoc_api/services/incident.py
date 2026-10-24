import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from autosoc_api.db.models.incident import Incident, IncidentStatus, IncidentSeverity
from autosoc_api.db.models.incident_note import IncidentNote
from autosoc_api.db.models.incident_timeline import IncidentTimeline
from autosoc_api.schemas.incident import IncidentBase, IncidentUpdate, IncidentNoteCreate

from sqlalchemy import desc

class IncidentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Incident]:
        result = await self.db.execute(select(Incident).order_by(desc(Incident.created_at)).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_id(self, incident_id: uuid.UUID) -> Incident:
        result = await self.db.execute(select(Incident).where(Incident.id == incident_id))
        incident = result.scalar_one_or_none()
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        return incident

    async def create_note(self, incident_id: uuid.UUID, note_in: IncidentNoteCreate, author_id: str) -> IncidentNote:
        # Verify incident exists
        await self.get_by_id(incident_id)
        
        note = IncidentNote(
            incident_id=incident_id,
            author_id=author_id,
            content=note_in.content
        )
        self.db.add(note)
        
        from autosoc_api.db.models.audit_log import AuditLog
        audit = AuditLog(
            actor_id=author_id,
            action="ADD_INCIDENT_NOTE",
            target_type="incident",
            target_id=str(incident_id),
            status="success"
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def get_notes(self, incident_id: uuid.UUID) -> List[IncidentNote]:
        result = await self.db.execute(select(IncidentNote).where(IncidentNote.incident_id == incident_id).order_by(IncidentNote.created_at.desc()))
        return list(result.scalars().all())
