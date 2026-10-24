import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

logger = logging.getLogger("ingestion.health_tracker")

class HealthTrackerService:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        # An in-memory buffer could be used to batch updates,
        # but for Phase 6 MVP, we will use a fire-and-forget task.

    async def update_source_health(self, source_id: str, status: str):
        """
        Updates the health state of the DataSource in Postgres.
        `status` can be: 'accepted', 'rejected', 'failed', 'duplicate'.
        """
        async def _do_update():
            try:
                from autosoc_api.db.models.data_source import DataSource, DataSourceHealth
                async for session in self.db_session_factory():
                    now = datetime.now(timezone.utc)
                    
                    if status == "accepted":
                        stmt = (
                            update(DataSource)
                            .where(DataSource.id == source_id)
                            .values(
                                last_received_at=now,
                                last_successful_ingestion=now,
                                success_count=DataSource.success_count + 1,
                                health_state=DataSourceHealth.HEALTHY
                            )
                        )
                    elif status in ["rejected", "failed"]:
                        stmt = (
                            update(DataSource)
                            .where(DataSource.id == source_id)
                            .values(
                                last_received_at=now,
                                last_failure_at=now,
                                failure_count=DataSource.failure_count + 1,
                                health_state=DataSourceHealth.DEGRADED
                            )
                        )
                    else: # duplicate
                        stmt = (
                            update(DataSource)
                            .where(DataSource.id == source_id)
                            .values(last_received_at=now)
                        )
                        
                    await session.execute(stmt)
                    await session.commit()
                    break
            except Exception as e:
                logger.error(f"Failed to update DataSource {source_id} health: {e}")
                
        # Fire and forget
        asyncio.create_task(_do_update())
