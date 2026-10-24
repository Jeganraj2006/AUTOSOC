import asyncio
import logging
import sys
from autosoc_detection.config import settings
from autosoc_detection.rules.registry import RuleRegistry
from autosoc_detection.state.manager import StateManager
from autosoc_detection.engine.core import DetectionEngine
from autosoc_detection.alerts.publisher import AlertPublisher
from autosoc_detection.alerts.persistence import AlertPersistence
from autosoc_detection.consumer import DetectionConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("autosoc_detection")

async def main():
    logger.info("Initializing Detection Worker...")
    
    # 1. Load Rules
    registry = RuleRegistry(settings.rules_dir)
    registry.load_rules()
    
    # 2. Setup State
    state_manager = StateManager(settings.redis_url)
    
    # 3. Setup Persistence & Publisher
    persistence = AlertPersistence(settings.database_url)
    publisher = AlertPublisher(settings.kafka_bootstrap_servers, settings.kafka_alert_topic)
    await publisher.start()
    
    # 4. Engine & Consumer
    engine = DetectionEngine(registry, state_manager)
    consumer = DetectionConsumer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_consumer_group,
        topic=settings.kafka_source_topic,
        engine=engine,
        publisher=publisher,
        persistence=persistence
    )
    
    from autosoc_detection.health import start_health_server
    
    try:
        await asyncio.gather(
            consumer.start(),
            start_health_server()
        )
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Fatal error in worker: {str(e)}")
    finally:
        await publisher.stop()
        await state_manager.close()
        await persistence.close()
        logger.info("Worker shut down cleanly.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down.")
