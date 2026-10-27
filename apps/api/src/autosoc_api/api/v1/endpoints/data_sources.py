from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import hashlib
import secrets

from autosoc_api.db.session import get_db_session
from autosoc_api.auth.models import Principal
from autosoc_api.auth.dependencies import require_permission
from autosoc_api.auth.permissions import Permissions
from autosoc_api.schemas.data_source import DataSourceResponse, DataSourceCreate, DataSourceUpdate, DataSourceListResponse, DataSourceProvisionedResponse
from autosoc_api.services.audit_service import audit_service
from autosoc_api.db.models.data_source import DataSource
from autosoc_api.db.repositories.base import BaseRepository

router = APIRouter()
ds_repo = BaseRepository(DataSource)


def generate_ingestion_api_key() -> tuple[str, str]:
    """Return an ingestion key and its SHA-256 database representation."""
    api_key = f"asoc_{secrets.token_urlsafe(32)}"
    return api_key, hashlib.sha256(api_key.encode("utf-8")).hexdigest()

@router.get("", response_model=DataSourceListResponse)
async def list_data_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    principal: Principal = Depends(require_permission(Permissions.DATASOURCES_READ)),
    db: AsyncSession = Depends(get_db_session)
):
    items = await ds_repo.get_multi(db, skip=skip, limit=limit)
    return {"items": items, "total": len(items)}

@router.post("", response_model=DataSourceProvisionedResponse)
async def create_data_source(
    ds_in: DataSourceCreate,
    principal: Principal = Depends(require_permission(Permissions.DATASOURCES_MANAGE)),
    db: AsyncSession = Depends(get_db_session)
):
    # The cleartext key is intentionally emitted only by this creation response.
    # The database keeps its SHA-256 hash, which the ingestion service verifies.
    api_key, api_key_hash = generate_ingestion_api_key()
    obj = await ds_repo.create(db, obj_in={**ds_in.model_dump(), "api_key_hash": api_key_hash})
    
    await audit_service.log(
        db, principal, action="create", target_type="data_source",
        status="success", target_id=str(obj.id)
    )
    return {**DataSourceResponse.model_validate(obj).model_dump(), "api_key": api_key}

@router.put("/{ds_id}", response_model=DataSourceResponse)
async def update_data_source(
    ds_id: UUID,
    ds_in: DataSourceUpdate,
    principal: Principal = Depends(require_permission(Permissions.DATASOURCES_MANAGE)),
    db: AsyncSession = Depends(get_db_session)
):
    obj = await ds_repo.get(db, str(ds_id))
    if not obj:
        raise HTTPException(status_code=404, detail="Data Source not found")
        
    updated_obj = await ds_repo.update(db, db_obj=obj, obj_in=ds_in.model_dump(exclude_unset=True))
    
    await audit_service.log(
        db, principal, action="update", target_type="data_source",
        status="success", target_id=str(obj.id)
    )
    return updated_obj


@router.post("/{ds_id}/revoke", response_model=DataSourceResponse)
async def revoke_data_source_key(
    ds_id: UUID,
    principal: Principal = Depends(require_permission(Permissions.DATASOURCES_MANAGE)),
    db: AsyncSession = Depends(get_db_session),
):
    """Irreversibly revoke a source ingestion key and disable the source.

    A replacement must be provisioned deliberately.  The cleartext key is
    never stored, so revocation cannot accidentally expose it or reactivate it.
    """
    obj = await ds_repo.get(db, str(ds_id))
    if not obj:
        raise HTTPException(status_code=404, detail="Data Source not found")

    await ds_repo.update(
        db,
        db_obj=obj,
        obj_in={"api_key_hash": None, "enabled": False},
    )
    await audit_service.log(
        db,
        principal,
        action="revoke_ingestion_key",
        target_type="data_source",
        status="success",
        target_id=str(obj.id),
    )
    return obj
