import uuid
import time
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel, Field
from typing import List, Optional

from autosoc_schemas.events.raw import IngestionStatus, IngestionResult
# In a real setup, pipeline and auth_service would be injected dependencies
# We assume they are initialized in main.py and attached to app.state
from autosoc_ingestion.services.auth import verify_api_key

router = APIRouter()

MAX_PAYLOAD_SIZE = 1024 * 512 # 512KB per event
MAX_BATCH_SIZE = 100

class BatchEventRequest(BaseModel):
    events: List[str] = Field(..., max_length=MAX_BATCH_SIZE, description="List of raw JSON strings")

async def get_pipeline(request: Request):
    return request.app.state.pipeline

async def get_db_session(request: Request):
    # Ingestion worker needs DB access to verify source credentials.
    # In a pure microservice, it might call the API, but here it has direct DB access.
    async for session in request.app.state.db_session_factory():
        yield session

async def verify_source(request: Request, x_api_key: str = Header(...), db=Depends(get_db_session)):
    from autosoc_api.db.models.data_source import DataSource
    from sqlalchemy import select
    from autosoc_ingestion.services.auth import verify_api_key
    
    # Simple lookup format: asoc_<random>
    # We would actually need to look up by an ID if we don't want to iterate all sources.
    # Better approach: pass source_id in header, or encode source_id in the API key.
    # For Phase 6 MVP, let's require X-Source-Id and X-Api-Key.
    
    source_id = request.headers.get("X-Source-Id")
    if not source_id:
        raise HTTPException(status_code=401, detail="X-Source-Id header required")
        
    stmt = select(DataSource).where(DataSource.id == source_id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=401, detail="Invalid source")
    if not source.enabled:
        raise HTTPException(status_code=403, detail="Source is disabled")
        
    if not source.api_key_hash or not verify_api_key(x_api_key, source.api_key_hash):
        raise HTTPException(status_code=401, detail="Invalid API key")
        
    rate_limiter = request.app.state.rate_limiter
    await rate_limiter.check_rate_limit(source_id)
    
    return source

@router.post("", response_model=IngestionStatus)
async def ingest_single_event(
    request: Request,
    source = Depends(verify_source),
    pipeline = Depends(get_pipeline),
    x_trace_id: Optional[str] = Header(None)
):
    body = await request.body()
    if len(body) > MAX_PAYLOAD_SIZE:
        raise HTTPException(status_code=413, detail="Payload too large")
        
    payload = body.decode('utf-8')
    ingestion_id = uuid.uuid4()
    
    status = await pipeline.process_event(
        payload=payload,
        source_id=str(source.id),
        source_name=source.name,
        source_type=source.source_type.value,
        content_type=request.headers.get("content-type", "application/json"),
        ingestion_method="http_json",
        ingestion_id=ingestion_id,
        trace_id=x_trace_id,
        request_id=getattr(request.state, "request_id", None)
    )
    
    if status.status == "failed":
        # 503 so the client retries
        raise HTTPException(status_code=503, detail=status.error)
        
    return status

@router.post("/batch", response_model=IngestionResult)
async def ingest_batch_events(
    request: Request,
    batch: BatchEventRequest,
    source = Depends(verify_source),
    pipeline = Depends(get_pipeline),
    x_trace_id: Optional[str] = Header(None)
):
    ingestion_id = uuid.uuid4()
    results = []
    accepted = 0
    rejected = 0
    duplicates = 0
    
    for event_str in batch.events:
        if len(event_str.encode('utf-8')) > MAX_PAYLOAD_SIZE:
            results.append(IngestionStatus(status="rejected", error="Payload too large"))
            rejected += 1
            continue
            
        status = await pipeline.process_event(
            payload=event_str,
            source_id=str(source.id),
            source_name=source.name,
            source_type=source.source_type.value,
            content_type="application/json",
            ingestion_method="http_json_batch",
            ingestion_id=ingestion_id,
            trace_id=x_trace_id,
            request_id=getattr(request.state, "request_id", None)
        )
        
        results.append(status)
        if status.status == "accepted":
            accepted += 1
        elif status.status == "duplicate":
            duplicates += 1
        else:
            rejected += 1
            
    return IngestionResult(
        ingestion_id=ingestion_id,
        received=len(batch.events),
        accepted=accepted,
        rejected=rejected,
        duplicates=duplicates,
        events=results
    )
