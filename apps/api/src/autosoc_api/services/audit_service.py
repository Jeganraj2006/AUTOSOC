from autosoc_api.db.repositories.audit_log import audit_repo
from sqlalchemy.ext.asyncio import AsyncSession
from autosoc_api.auth.models import Principal
from typing import Dict, Any, Optional

class AuditService:
    """
    Service layer for audit logging, ensuring separation of business logic from repository.
    """
    async def log(
        self,
        db: AsyncSession,
        principal: Principal,
        action: str,
        target_type: str,
        status: str,
        target_id: Optional[str] = None,
        request_id: Optional[str] = None,
        source_ip: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        return await audit_repo.log_action(
            db=db,
            actor_id=principal.subject_id,
            actor_name=principal.username,
            actor_roles=principal.roles,
            action=action,
            target_type=target_type,
            status=status,
            target_id=target_id,
            request_id=request_id,
            source_ip=source_ip,
            reason=reason,
            metadata=metadata
        )

audit_service = AuditService()
