from sqlalchemy.ext.asyncio import AsyncSession
from autosoc_api.db.models.audit_log import AuditLog

async def audit_log(db: AsyncSession, user_id: str, action: str, description: str, status: str = "success"):
    try:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            description=description,
            status=status
        )
        db.add(log_entry)
        await db.commit()
    except Exception as e:
        # Avoid crashing the main action if audit fails, but log it heavily
        import logging
        logging.error(f"Failed to write audit log: {e}")
