from autosoc_api.db.repositories.base import BaseRepository
from autosoc_api.db.models.audit_log import AuditLog
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import json

class AuditLogRepository(BaseRepository[AuditLog]):
    async def log_action(
        self,
        db: AsyncSession,
        actor_id: str,
        actor_name: str,
        actor_roles: list[str],
        action: str,
        target_type: str,
        status: str,
        target_id: Optional[str] = None,
        request_id: Optional[str] = None,
        source_ip: Optional[str] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Creates an append-only audit log entry.
        """
        roles_str = ",".join(actor_roles) if actor_roles else ""
        
        # We ensure metadata is serializable if not natively handled by SQLAlchemy JSONB
        
        audit_in = {
            "actor_id": actor_id,
            "actor_name": actor_name,
            "actor_roles": roles_str,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "status": status,
            "request_id": request_id,
            "source_ip": source_ip,
            "reason": reason,
            "metadata_json": metadata
        }
        
        return await self.create(db, obj_in=audit_in)

audit_repo = AuditLogRepository(AuditLog)
