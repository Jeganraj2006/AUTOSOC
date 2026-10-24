import logging
from typing import List, Dict, Any
from datetime import datetime
from autosoc_correlation.rules.rule_models import CorrelationRule
from autosoc_api.db.models.incident import Incident, IncidentStatus, IncidentSeverity
from autosoc_api.db.models.incident_alert import IncidentAlert
from autosoc_schemas.events.incident import IncidentCreated, IncidentUpdated
from sqlalchemy.orm import Session
# Note: we should use async pg in real app, but for worker simplicity we could use a synchronous session
# or async session depending on the database config used by the worker. We will mock the database insert for now 
# focus on publishing the message to Kafka.

logger = logging.getLogger(__name__)

class IncidentManager:
    @staticmethod
    async def create_incident(incident_id: str, alerts: List[Dict[str, Any]], entity_id: str, new_score: float, rule: CorrelationRule):
        logger.info(f"Creating incident {incident_id} triggered by rule {rule.id}")
        
        incident_event = IncidentCreated(
            incident_id=incident_id,
            title=f"Correlated Activity: {rule.name} on {entity_id}",
            status=IncidentStatus.NEW.value,
            severity=rule.severity,
            risk_score=new_score,
            alert_count=len(alerts),
            primary_entities=[{"role": "primary", "value": entity_id}],
            updated_at=datetime.utcnow(),
            schema_version=1
        )
        
        # Publish event
        # (Assuming app and publisher are properly initialized)
        try:
            # Here we just mock the DB insert or actually write to Postgres.
            # For the worker, we will just publish the event and let the API handle DB later,
            # or the worker itself writes to the DB. The requirement says:
            # "Creates a new Incident in PostgreSQL when a threshold is met."
            # We will implement DB writing in a separate function.
            pass
        except Exception as e:
            logger.error(f"Failed to create incident in DB: {e}")
            
        # We will directly call publish_incident if we can
        # For fastkafka, we return it from the producer function.
        # So we need to put it into a queue or call the producer.
        pass

    @staticmethod
    async def update_incident(incident_id: str, alerts: List[Dict[str, Any]], new_score: float, rule: CorrelationRule):
        logger.info(f"Updating incident {incident_id} triggered by rule {rule.id}")
        
        incident_event = IncidentUpdated(
            incident_id=incident_id,
            title=f"Correlated Activity: {rule.name}",
            status=IncidentStatus.INVESTIGATING.value, # Auto-transition if more alerts arrive?
            severity=rule.severity,
            risk_score=new_score,
            alert_count=len(alerts),
            primary_entities=[],
            updated_at=datetime.utcnow(),
            schema_version=1
        )
        pass
