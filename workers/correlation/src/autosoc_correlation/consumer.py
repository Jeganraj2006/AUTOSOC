import logging
from fastkafka import FastKafka
from autosoc_schemas.events.detection import DetectionResult
from autosoc_correlation.engine.correlator import correlate_alert

logger = logging.getLogger(__name__)

def setup_consumer(app: FastKafka):
    @app.consumes(topic="security.alerts", auto_offset_reset="latest")
    async def on_alert(msg: DetectionResult):
        logger.info(f"Consumed Alert: {msg.detection_id}")
        await correlate_alert(msg)
