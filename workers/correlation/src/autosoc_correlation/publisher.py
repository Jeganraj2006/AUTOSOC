import logging
from fastkafka import FastKafka
from autosoc_schemas.events.incident import IncidentCreated, IncidentUpdated

logger = logging.getLogger(__name__)

def setup_publisher(app: FastKafka):
    @app.produces(topic="security.incidents")
    async def publish_incident(incident_event: IncidentCreated | IncidentUpdated) -> IncidentCreated | IncidentUpdated:
        logger.info(f"Publishing incident event for {incident_event.incident_id}")
        return incident_event

    return publish_incident
