from fastapi import APIRouter
from autosoc_api.api.v1.endpoints import audit, auth, events, health, data_sources, rules, alerts, incidents, predictions, agents, responses, system

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(data_sources.router, prefix="/data-sources", tags=["data-sources"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(predictions.router, prefix="/incidents", tags=["predictions"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(agents.router, prefix="", tags=["agents"])
api_router.include_router(responses.router, prefix="", tags=["responses"])
