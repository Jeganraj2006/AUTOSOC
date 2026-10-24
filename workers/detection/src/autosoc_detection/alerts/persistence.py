import uuid
import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from autosoc_schemas.events.detection import DetectionResult

class AlertPersistence:
    def __init__(self, database_url: str):
        # We assume the database schemas are already managed by the API's alembic migrations
        self.engine = create_async_engine(database_url, pool_size=5, max_overflow=10)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def close(self):
        await self.engine.dispose()

    async def persist_alert(self, result: DetectionResult):
        async with self.session_factory() as session:
            # We execute raw SQL to avoid dependency on the API's SQLAlchemy models inside the worker,
            # ensuring decoupling.
            
            # Map severity properly
            severity = result.severity.lower()
            if severity not in ["low", "medium", "high", "critical"]:
                severity = "low"
                
            entities_json = [e.model_dump() for e in result.entities]
            
            query = text("""
                INSERT INTO alerts (
                    id, title, description, severity, status, 
                    source_event_id, rule_id, indicators_json, 
                    created_at, updated_at
                ) VALUES (
                    :id, :title, :description, :severity, :status,
                    :source_event_id, :rule_id, :indicators_json,
                    :created_at, :updated_at
                )
            """)
            
            await session.execute(query, {
                "id": str(uuid.uuid4()),
                "title": result.title,
                "description": result.description,
                "severity": severity,
                "status": "new",
                "source_event_id": str(result.event_ids[0]) if result.event_ids else None,
                "rule_id": result.rule_id, # Requires rule_metadata id to match, or we bypass foreign key if it's relaxed.
                "indicators_json": entities_json,
                "created_at": datetime.datetime.now(datetime.timezone.utc),
                "updated_at": datetime.datetime.now(datetime.timezone.utc)
            })
            
            await session.commit()
