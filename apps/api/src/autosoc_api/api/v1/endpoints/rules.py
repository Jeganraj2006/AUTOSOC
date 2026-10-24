from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from autosoc_api.db.session import get_db_session
from autosoc_api.auth.models import Principal
from autosoc_api.auth.dependencies import require_permission
from autosoc_api.auth.permissions import Permissions
from autosoc_api.schemas.rule_metadata import RuleMetadataResponse, RuleMetadataCreate, RuleMetadataUpdate
from autosoc_api.services.audit_service import audit_service
from autosoc_api.db.models.rule_metadata import DetectionRuleMetadata
from autosoc_api.db.repositories.base import BaseRepository

router = APIRouter()
rule_repo = BaseRepository(DetectionRuleMetadata)

@router.get("", response_model=List[RuleMetadataResponse])
async def list_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    principal: Principal = Depends(require_permission(Permissions.RULES_READ)),
    db: AsyncSession = Depends(get_db_session)
):
    return await rule_repo.get_multi(db, skip=skip, limit=limit)

@router.post("", response_model=RuleMetadataResponse)
async def create_rule(
    rule_in: RuleMetadataCreate,
    principal: Principal = Depends(require_permission(Permissions.RULES_MANAGE)),
    db: AsyncSession = Depends(get_db_session)
):
    obj = await rule_repo.create(db, obj_in=rule_in.model_dump())
    
    await audit_service.log(
        db, principal, action="create", target_type="rule",
        status="success", target_id=str(obj.id)
    )
    return obj
