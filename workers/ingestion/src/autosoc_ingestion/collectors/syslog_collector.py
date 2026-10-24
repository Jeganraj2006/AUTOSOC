import asyncio
import logging
import uuid
import time
from autosoc_ingestion.services.pipeline import IngestionPipeline
from autosoc_ingestion.services.rate_limiter import RateLimiterService
from autosoc_ingestion.services.auth import verify_api_key

logger = logging.getLogger("ingestion.syslog")

class SyslogProtocol(asyncio.DatagramProtocol):
    def __init__(self, pipeline: IngestionPipeline, source_id: str, source_name: str, rate_limiter: RateLimiterService):
        self.pipeline = pipeline
        self.source_id = source_id
        self.source_name = source_name
        self.rate_limiter = rate_limiter
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport
        logger.info(f"Syslog UDP server bound")

    def datagram_received(self, data: bytes, addr):
        # Fire and forget processing for UDP
        asyncio.create_task(self.process_syslog_msg(data, addr))

    async def process_syslog_msg(self, data: bytes, addr):
        try:
            # UDP doesn't guarantee auth headers, so in this MVP the Syslog listener
            # is statically bound to a specific source_id (representing the syslog forwarder).
            # In a real environment, it would be secured via mTLS on TCP.
            
            await self.rate_limiter.check_rate_limit(self.source_id)
            
            payload = data.decode('utf-8', errors='replace')
            
            # Very basic Syslog parser could go here just to extract transport metadata,
            # but we preserve the full raw payload.
            
            await self.pipeline.process_event(
                payload=payload,
                source_id=self.source_id,
                source_name=self.source_name,
                source_type="linux_syslog",
                content_type="text/plain",
                ingestion_method="syslog_udp",
                ingestion_id=uuid.uuid4(),
                trace_id=None,
                request_id=f"syslog-{int(time.time()*1000)}"
            )
        except Exception as e:
            logger.error(f"Failed to process syslog message from {addr}: {e}")

async def start_syslog_server(host: str, port: int, pipeline: IngestionPipeline, source_id: str, source_name: str, rate_limiter: RateLimiterService):
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: SyslogProtocol(pipeline, source_id, source_name, rate_limiter),
        local_addr=(host, port)
    )
    return transport
