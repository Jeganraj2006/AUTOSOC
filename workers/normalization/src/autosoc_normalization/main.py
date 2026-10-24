import asyncio
import logging
import signal
import sys
from autosoc_normalization.config import settings
from autosoc_normalization.registry import parser_registry
from autosoc_normalization.consumer import NormalizationConsumer
from autosoc_normalization.publisher import EventPublisher
from autosoc_normalization.storage.opensearch import OpenSearchStorage

# Import all parsers to register them
from autosoc_normalization.parsers import (
    SyntheticParser,
    HttpJsonParser,
    SyslogParser,
    WindowsEventParser,
    NetworkFlowParser,
    KubernetesAuditParser,
    CloudTrailParser
)

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger("autosoc_normalization")

def register_parsers():
    parser_registry.register("synthetic", SyntheticParser())
    parser_registry.register("http_json", HttpJsonParser())
    parser_registry.register("syslog", SyslogParser())
    parser_registry.register("windows_event", WindowsEventParser())
    parser_registry.register("network_flow", NetworkFlowParser())
    parser_registry.register("kubernetes_audit", KubernetesAuditParser())
    parser_registry.register("aws_cloudtrail", CloudTrailParser())
    logger.info("Registered all parsers.")

async def main():
    logger.info("Starting AutoSOC Normalization Worker")
    register_parsers()
    
    publisher = EventPublisher()
    opensearch = OpenSearchStorage(settings.OPENSEARCH_HOSTS)
    consumer = NormalizationConsumer(publisher, opensearch)
    
    await opensearch.initialize_templates()
    await publisher.start()
    
    # Setup graceful shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def shutdown():
        logger.info("Initiating graceful shutdown...")
        stop_event.set()

    if sys.platform != "win32":
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, shutdown)
            
    # Start consumer as a task
    consumer_task = asyncio.create_task(consumer.start())
    
    try:
        await stop_event.wait()
    except KeyboardInterrupt:
        pass
    finally:
        await consumer.stop()
        await consumer_task
        await publisher.stop()
        await opensearch.close()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
