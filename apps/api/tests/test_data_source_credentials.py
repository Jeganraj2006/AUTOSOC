import hashlib
from types import SimpleNamespace
from uuid import uuid4

import pytest

from autosoc_api.api.v1.endpoints import data_sources
from autosoc_api.api.v1.endpoints.data_sources import generate_ingestion_api_key
from autosoc_api.auth.models import Principal
from autosoc_api.schemas.data_source import DataSourceResponse


def test_generated_ingestion_key_is_high_entropy_and_only_hash_is_persistable() -> None:
    first_key, first_hash = generate_ingestion_api_key()
    second_key, second_hash = generate_ingestion_api_key()

    assert first_key.startswith("asoc_")
    assert len(first_key.removeprefix("asoc_")) >= 43
    assert first_key != second_key
    assert first_hash == hashlib.sha256(first_key.encode("utf-8")).hexdigest()
    assert second_hash == hashlib.sha256(second_key.encode("utf-8")).hexdigest()
    assert first_key not in first_hash


def test_read_model_does_not_expose_persisted_key_hash() -> None:
    assert "api_key_hash" not in DataSourceResponse.model_fields


@pytest.mark.asyncio
async def test_revocation_clears_the_hash_disables_source_and_writes_audit(monkeypatch: pytest.MonkeyPatch) -> None:
    source = SimpleNamespace(id=uuid4(), api_key_hash="stored-hash", enabled=True)
    updates: list[dict[str, object]] = []
    audits: list[dict[str, object]] = []

    class FakeRepository:
        async def get(self, _db: object, _id: str) -> object:
            return source

        async def update(self, _db: object, *, db_obj: object, obj_in: dict[str, object]) -> object:
            updates.append(obj_in)
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            return db_obj

    async def record_audit(_db: object, _principal: Principal, **kwargs: object) -> None:
        audits.append(kwargs)

    monkeypatch.setattr(data_sources, "ds_repo", FakeRepository())
    monkeypatch.setattr(data_sources.audit_service, "log", record_audit)
    result = await data_sources.revoke_data_source_key(
        source.id,
        principal=Principal(subject_id="admin", username="admin", roles=["administrator"], issuer="test"),
        db=object(),
    )

    assert result is source
    assert updates == [{"api_key_hash": None, "enabled": False}]
    assert source.api_key_hash is None
    assert source.enabled is False
    assert audits[0]["action"] == "revoke_ingestion_key"
