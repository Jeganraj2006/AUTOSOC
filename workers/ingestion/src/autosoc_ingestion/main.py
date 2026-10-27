import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_client import make_asgi_app

from autosoc_ingestion.config import settings
from autosoc_ingestion.collectors.http_collector import router as http_router
from autosoc_ingestion.collectors.samples_collector import router as samples_router
from autosoc_ingestion.publishers.redpanda import RedpandaPublisher
from autosoc_ingestion.archive.minio_archive import MinioArchiveService
from autosoc_ingestion.deduplication.redis_dedup import DeduplicationService
from autosoc_ingestion.services.pipeline import IngestionPipeline
from autosoc_ingestion.services.rate_limiter import RateLimiterService
from autosoc_ingestion.services.health_tracker import HealthTrackerService
from autosoc_api.db.session import AsyncSessionLocal

logger = logging.getLogger("ingestion.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize infrastructure connections
    app.state.publisher = RedpandaPublisher(
        bootstrap_servers=settings.REDPANDA_BROKERS,
        raw_topic=settings.REDPANDA_RAW_TOPIC,
        failed_topic=settings.REDPANDA_FAILED_TOPIC
    )
    await app.state.publisher.connect()

    app.state.archive = MinioArchiveService(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        bucket_name=settings.MINIO_BUCKET,
        secure=settings.MINIO_SECURE
    )

    app.state.dedup = DeduplicationService(
        redis_url=settings.REDIS_URL,
        ttl_seconds=settings.DEDUP_TTL_SECONDS
    )
    await app.state.dedup.connect()
    
    app.state.rate_limiter = RateLimiterService(
        redis_url=settings.REDIS_URL,
        limit_per_minute=settings.RATE_LIMIT_PER_MINUTE
    )
    await app.state.rate_limiter.connect()

    # We reuse the autosoc_api DB session factory since we're in the same monorepo
    async def get_db_session():
        async with AsyncSessionLocal() as session:
            yield session
            
    app.state.db_session_factory = get_db_session
    
    app.state.health_tracker = HealthTrackerService(db_session_factory=app.state.db_session_factory)

    app.state.pipeline = IngestionPipeline(
        publisher=app.state.publisher,
        archive=app.state.archive,
        dedup=app.state.dedup,
        health_tracker=app.state.health_tracker,
        retry_max_attempts=settings.RETRY_MAX_ATTEMPTS,
        retry_base_delay_seconds=settings.RETRY_BASE_DELAY_SECONDS,
        retry_max_delay_seconds=settings.RETRY_MAX_DELAY_SECONDS,
    )

    yield

    # Cleanup
    await app.state.publisher.disconnect()
    await app.state.dedup.disconnect()
    
app = FastAPI(title="AutoSOC Ingestion API", version="0.1.0", lifespan=lifespan)

# Metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Health endpoints
@app.get("/health/live")
async def liveness():
    return {"status": "ok"}

@app.get("/health/ready")
async def readiness():
    # Ping dependencies
    redis_ok = app.state.dedup.client is not None
    rp_ok = app.state.publisher.producer is not None
    if not (redis_ok and rp_ok):
        return {"status": "degraded", "redis": redis_ok, "redpanda": rp_ok}
    return {"status": "ready"}

# Include collector routers
app.include_router(http_router, prefix="/api/v1/ingest/events", tags=["ingestion"])
app.include_router(samples_router, prefix="/api/v1/ingest/samples", tags=["samples"])
