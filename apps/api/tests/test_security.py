import uuid

import jwt
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from autosoc_api.auth.dependencies import get_current_principal
from autosoc_api.auth.keycloak import validator
from autosoc_api.auth.models import Principal
from autosoc_api.auth.permissions import get_permissions_for_roles
from autosoc_api.core.config import Settings
from autosoc_api.main import app


client = TestClient(app)


def test_missing_token_is_unauthorized_for_events() -> None:
    response = client.get("/api/v1/events/")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_missing_token_is_unauthorized_for_incident_mutation() -> None:
    response = client.patch(f"/api/v1/incidents/{uuid.uuid4()}/status?status=triaged")
    assert response.status_code == 401


def test_insufficient_role_cannot_mutate_incident() -> None:
    auditor = Principal(
        subject_id="auditor-id",
        username="auditor",
        roles=["auditor"],
        permissions=get_permissions_for_roles(["auditor"]),
        issuer="https://issuer.example/realms/autosoc",
    )
    app.dependency_overrides[get_current_principal] = lambda: auditor
    try:
        response = client.patch(f"/api/v1/incidents/{uuid.uuid4()}/status?status=triaged")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 403


def test_jwks_failure_does_not_create_a_privileged_principal(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_jwks(_: str) -> None:
        raise RuntimeError("JWKS unavailable")

    monkeypatch.setattr(validator._jwks_client, "get_signing_key_from_jwt", fail_jwks)
    with pytest.raises(HTTPException) as exc_info:
        validator.validate_token("not-a-token")
    assert exc_info.value.status_code == 401


def test_expired_token_is_unauthorized(monkeypatch: pytest.MonkeyPatch) -> None:
    class SigningKey:
        key = "unused"

    monkeypatch.setattr(
        validator._jwks_client, "get_signing_key_from_jwt", lambda _: SigningKey()
    )

    def expired_decode(*_: object, **__: object) -> None:
        raise jwt.ExpiredSignatureError("expired")

    monkeypatch.setattr("autosoc_api.auth.keycloak.jwt.decode", expired_decode)
    with pytest.raises(HTTPException) as exc_info:
        validator.validate_token("expired-token")
    assert exc_info.value.status_code == 401


def test_empty_keycloak_audience_is_rejected_by_configuration() -> None:
    with pytest.raises(ValidationError):
        Settings(KEYCLOAK_AUDIENCE="")
