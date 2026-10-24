import asyncio
import uuid
import sys
from datetime import datetime
import json
from autosoc_api.db.session import SessionLocal
from autosoc_api.db.models.incident import Incident, IncidentStatus
from autosoc_api.db.models.audit_log import AuditLog
from autosoc_api.services.incident_transition import IncidentTransitionService

async def main():
    async with SessionLocal() as db:
        # Create an Incident
        inc_id = uuid.uuid4()
        inc = Incident(
            id=inc_id,
            title="Test Incident",
            description="Testing Incident creation",
            severity="high",
            status=IncidentStatus.NEW.value,
            risk_score=75.0,
            alert_count=3,
            event_count=10,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(inc)
        await db.commit()
        
        print(f"Created incident: {inc.id}")
        
        # Test transition
        transition_service = IncidentTransitionService(db)
        try:
            updated_inc = await transition_service.update_status(
                incident_id=inc_id,
                new_status=IncidentStatus.INVESTIGATING,
                user_id="test_admin"
            )
            print(f"Updated incident status to: {updated_inc.status}")
        except Exception as e:
            print(f"Error updating status: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
