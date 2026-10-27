import asyncio

import httpx
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from autosoc_api.auth.dependencies import require_permission
from autosoc_api.auth.models import Principal
from autosoc_api.auth.permissions import Permissions
from autosoc_api.db.models.agent_execution import AgentExecution, AgentExecutionStatus
from autosoc_api.db.session import AsyncSessionLocal, get_db_session
from autosoc_api.schemas.health import HealthResponse, VersionResponse
from autosoc_api.schemas.search import OperationalComponent, OperationalHealthResponse
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


async def _check_http_service(url: str) -> str:
    """A non-2xx auth response still proves the service is reachable."""
    try:
        async with httpx.AsyncClient(timeout=settings.HEALTH_CHECK_TIMEOUT_SECONDS) as client:
            response = await client.get(url)
        return "ok" if response.status_code < 500 else "unavailable"
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


@router.get("/operations", response_model=OperationalHealthResponse)
async def get_operational_health(
    db: AsyncSession = Depends(get_db_session),
    current_user: Principal = Depends(require_permission(Permissions.SETTINGS_READ)),
) -> OperationalHealthResponse:
    """Expose only directly observed dependency and persisted-run state.

    Workers do not currently persist heartbeats, so a running container is not
    represented as healthy.  That limitation is returned to the UI instead of
    being masked by an inferred status.
    """
    from datetime import datetime, timezone

    database, redis, opensearch, redpanda, ollama, object_storage = await asyncio.gather(
        _check_database(),
        _check_tcp(settings.REDIS_HOST, settings.REDIS_PORT),
        _check_opensearch(),
        _check_tcp(settings.REDPANDA_HOST, settings.REDPANDA_PORT),
        _check_http_service(f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags"),
        _check_http_service(settings.OBJECT_STORAGE_HEALTH_URL),
    )
    latest_execution_result = await db.execute(
        select(AgentExecution).order_by(AgentExecution.created_at.desc()).limit(1)
    )
    latest_execution = latest_execution_result.scalar_one_or_none()
    failed_count_result = await db.execute(
        select(func.count()).select_from(AgentExecution).where(AgentExecution.status == AgentExecutionStatus.FAILED)
    )
    failed_count = failed_count_result.scalar_one()

    def dependency_component(name: str, result: str) -> OperationalComponent:
        return OperationalComponent(
            name=name,
            status="healthy" if result == "ok" else "unavailable",
            detail="Direct connectivity check",
        )

    worker_names = (
        "ingestion worker",
        "normalization worker",
        "detection worker",
        "correlation worker",
        "prediction worker",
        "AI investigation worker",
    )
    components = [
        dependency_component("PostgreSQL", database),
        dependency_component("Redis", redis),
        dependency_component("Redpanda", redpanda),
        dependency_component("OpenSearch", opensearch),
        dependency_component("Object storage", object_storage),
        OperationalComponent(
            name="Ollama",
            status="healthy" if ollama == "ok" else "unavailable",
            detail="Direct provider connectivity check",
            model_identifier=latest_execution.model_name if latest_execution else None,
        ),
    ]
    components.extend(
        OperationalComponent(
            name=name,
            status="unknown",
            detail="No persisted worker heartbeat or broker-lag metric is available.",
            last_successful_operation=(latest_execution.completed_at if name == "AI investigation worker" and latest_execution else None),
            last_heartbeat=None,
            failed_processing_count=(failed_count if name == "AI investigation worker" else None),
            retry_or_dlq_count=None,
            model_identifier=(latest_execution.model_name if name == "AI investigation worker" and latest_execution else None),
        )
        for name in worker_names
    )
    return OperationalHealthResponse(
        components=components,
        checked_at=datetime.now(timezone.utc),
        limitations=[
            "Worker containers do not publish durable heartbeats, retry counters, or DLQ counts yet; worker health is therefore unknown.",
            "Dependency state is a point-in-time connectivity check, not proof of message consumption.",
        ],
    )
