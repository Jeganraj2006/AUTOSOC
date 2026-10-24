from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from autosoc_api.db.session import get_db_session
from autosoc_api.auth.models import Principal
from autosoc_api.auth.dependencies import require_permission
from autosoc_api.auth.permissions import Permissions
from autosoc_api.schemas.data_source import DataSourceResponse, DataSourceCreate, DataSourceUpdate, DataSourceListResponse
from autosoc_api.services.audit_service import audit_service
from autosoc_api.db.models.data_source import DataSource
from autosoc_api.db.repositories.base import BaseRepository

router = APIRouter()
ds_repo = BaseRepository(DataSource)

@router.get("", response_model=DataSourceListResponse)
async def list_data_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    principal: Principal = Depends(require_permission(Permissions.DATASOURCES_READ)),
    db: AsyncSession = Depends(get_db_session)
):
    items = await ds_repo.get_multi(db, skip=skip, limit=limit)
    return {"items": items, "total": len(items)}

@router.post("", response_model=DataSourceResponse)
async def create_data_source(
    ds_in: DataSourceCreate,
    principal: Principal = Depends(require_permission(Permissions.DATASOURCES_MANAGE)),
    db: AsyncSession = Depends(get_db_session)
):
    obj = await ds_repo.create(db, obj_in=ds_in.model_dump())
    
    await audit_service.log(
        db, principal, action="create", target_type="data_source",
        status="success", target_id=str(obj.id)
    )
    return obj

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
