import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from autosoc_api.db.models.incident import Incident, IncidentStatus
from autosoc_api.services.incident import IncidentService

class IncidentTransitionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.incident_service = IncidentService(db)

    async def update_status(self, incident_id: uuid.UUID, new_status: IncidentStatus, user_id: str, reason: Optional[str] = None) -> Incident:
        incident = await self.incident_service.get_by_id(incident_id)
        
        # Define allowed transitions
        # Simplistic approach for now
        allowed_transitions = {
            IncidentStatus.NEW: [IncidentStatus.TRIAGED, IncidentStatus.FALSE_POSITIVE, IncidentStatus.CLOSED],
            IncidentStatus.TRIAGED: [IncidentStatus.INVESTIGATING, IncidentStatus.FALSE_POSITIVE, IncidentStatus.CLOSED],
            IncidentStatus.INVESTIGATING: [IncidentStatus.AWAITING_APPROVAL, IncidentStatus.CONTAINED, IncidentStatus.RESOLVED],
            IncidentStatus.AWAITING_APPROVAL: [IncidentStatus.CONTAINED, IncidentStatus.RESOLVED, IncidentStatus.INVESTIGATING],
            IncidentStatus.CONTAINED: [IncidentStatus.RESOLVED],
            IncidentStatus.RESOLVED: [IncidentStatus.CLOSED],
            IncidentStatus.FALSE_POSITIVE: [IncidentStatus.NEW],
            IncidentStatus.CLOSED: [IncidentStatus.NEW, IncidentStatus.INVESTIGATING]
        }
        
        if new_status not in allowed_transitions.get(incident.status, []):
            raise HTTPException(status_code=400, detail=f"Invalid transition from {incident.status} to {new_status}")
            
        old_status = incident.status
        incident.status = new_status
        if new_status == IncidentStatus.FALSE_POSITIVE and reason:
            incident.false_positive_reason = reason
        if new_status == IncidentStatus.CLOSED and reason:
            incident.closure_reason = reason
            
        from autosoc_api.db.models.audit_log import AuditLog
        audit = AuditLog(
            actor_id=user_id,
            action="UPDATE_INCIDENT_STATUS",
            target_type="incident",
            target_id=str(incident_id),
            status="success",
            metadata_json={"old_status": old_status.value, "new_status": new_status.value}
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self.db.refresh(incident)
        return incident
