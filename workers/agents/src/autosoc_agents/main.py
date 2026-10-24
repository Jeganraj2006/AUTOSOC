import os
import asyncio
import logging
from autosoc_agents.orchestrator.graph import build_investigation_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting AutoSOC Agent Worker...")
    # In a full deployment, this would connect to Redpanda and consume
    # incident investigation requests. For MVP, we just initialize the graph.
    graph = build_investigation_graph()
    logger.info("Graph initialized successfully.")
    
    # Keep alive
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
