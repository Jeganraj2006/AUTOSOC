import pytest
from fastapi.testclient import TestClient
from autosoc_api.main import app
from autosoc_api.api.v1.endpoints import health
from autosoc_api.core.config import settings

client = TestClient(app)

def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == settings.PROJECT_NAME
    assert any(phase in data["phase"] for phase in ["Phase 5", "Phase 7"])

def test_health_live() -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"

def test_health_ready_when_dependencies_are_available(monkeypatch: pytest.MonkeyPatch) -> None:
    async def healthy_dependencies() -> dict[str, str]:
        return {"database": "ok", "redis": "ok", "opensearch": "ok", "redpanda": "ok"}

    monkeypatch.setattr(health, "check_dependencies", healthy_dependencies)
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["components"]["database"] == "ok"


def test_health_ready_reports_unavailable_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    async def unavailable_dependencies() -> dict[str, str]:
        return {"database": "unavailable", "redis": "ok", "opensearch": "ok", "redpanda": "ok"}

    monkeypatch.setattr(health, "check_dependencies", unavailable_dependencies)
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["dependencies"]["database"] == "unavailable"

def test_version() -> None:
    response = client.get("/api/v1/health/version")
    assert response.status_code == 200
    assert response.json()["app_version"] == "0.1.0-dev"

def test_request_id_injected() -> None:
    response = client.get("/")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0
