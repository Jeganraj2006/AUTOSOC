import asyncio

import httpx
from fastapi import APIRouter, Response, status
from sqlalchemy import text

from autosoc_api.db.session import AsyncSessionLocal
from autosoc_api.schemas.health import HealthResponse, VersionResponse
from autosoc_api.core.config import settings

router = APIRouter()


async def _check_database() -> str:
    try:
        async with AsyncSessionLocal() as session:
            await asyncio.wait_for(session.execute(text("SELECT 1")), settings.HEALTH_CHECK_TIMEOUT_SECONDS)
        return "ok"
    except Exception:
        return "unavailable"


async def _check_tcp(host: str, port: int) -> str:
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), settings.HEALTH_CHECK_TIMEOUT_SECONDS
        )
        writer.close()
        await writer.wait_closed()
        return "ok"
    except Exception:
        return "unavailable"


async def _check_opensearch() -> str:
    try:
        async with httpx.AsyncClient(timeout=settings.HEALTH_CHECK_TIMEOUT_SECONDS) as client:
            response = await client.get(settings.OPENSEARCH_HOSTS)
        return "ok" if response.is_success else "unavailable"
    except httpx.HTTPError:
        return "unavailable"


async def check_dependencies() -> dict[str, str]:
    """Check backing services used by the API without asserting their health."""
    database, redis, opensearch, redpanda = await asyncio.gather(
        _check_database(),
        _check_tcp(settings.REDIS_HOST, settings.REDIS_PORT),
        _check_opensearch(),
        _check_tcp(settings.REDPANDA_HOST, settings.REDPANDA_PORT),
    )
    return {
        "database": database,
        "redis": redis,
        "opensearch": opensearch,
        "redpanda": redpanda,
    }

@router.get("/live", response_model=HealthResponse)
def get_liveness() -> HealthResponse:
    """Check if the API process is running."""
    return HealthResponse(
        status="alive",
        components={"api": "ok"},
        dependencies={}
    )

@router.get("/ready", response_model=HealthResponse)
async def get_readiness(response: Response) -> HealthResponse:
    """Check if the API is ready to accept traffic."""
    dependencies = await check_dependencies()
    is_ready = all(component == "ok" for component in dependencies.values())
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(
        status="ready" if is_ready else "not_ready",
        components={"api": "ok", **dependencies},
        dependencies=dependencies,
    )

@router.get("/version", response_model=VersionResponse)
def get_version() -> VersionResponse:
    """Get application version information."""
    return VersionResponse(
        app_name=settings.PROJECT_NAME,
        app_version=settings.APP_VERSION,
        api_version=settings.API_VERSION,
        environment=settings.ENVIRONMENT,
        commit_id=settings.COMMIT_ID
    )
