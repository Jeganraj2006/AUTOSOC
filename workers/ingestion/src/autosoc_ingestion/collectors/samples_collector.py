import json
import uuid
from typing import Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
from autosoc_ingestion.collectors.http_collector import verify_source, get_pipeline, MAX_PAYLOAD_SIZE
from autosoc_schemas.events.raw import IngestionResult, IngestionStatus

router = APIRouter()

class CloudTrailBatch(BaseModel):
    Records: list[Dict[str, Any]]

@router.post("/cloudtrail", response_model=IngestionResult)
async def ingest_cloudtrail_sample(
    request: Request,
    batch: CloudTrailBatch,
    source = Depends(verify_source),
    pipeline = Depends(get_pipeline),
    x_trace_id: Optional[str] = Header(None)
):
    """
    Ingest an AWS CloudTrail sample payload.
    CloudTrail logs come wrapped in a {"Records": [...]} array.
    """
    if source.source_type.value != "aws_cloudtrail":
        raise HTTPException(status_code=400, detail="Invalid source type for CloudTrail ingestion")
        
    ingestion_id = uuid.uuid4()
    results = []
    
    for record in batch.Records:
        event_str = json.dumps(record)
        if len(event_str.encode('utf-8')) > MAX_PAYLOAD_SIZE:
            results.append(IngestionStatus(status="rejected", error="Payload too large"))
            continue
            
        status = await pipeline.process_event(
            payload=event_str,
            source_id=str(source.id),
            source_name=source.name,
            source_type=source.source_type.value,
            content_type="application/json",
            ingestion_method="http_cloudtrail_sample",
            ingestion_id=ingestion_id,
            trace_id=x_trace_id,
            request_id=getattr(request.state, "request_id", None)
        )
        results.append(status)
        
    accepted = sum(1 for r in results if r.status == "accepted")
    rejected = sum(1 for r in results if r.status == "rejected")
    duplicates = sum(1 for r in results if r.status == "duplicate")
    
    return IngestionResult(
        ingestion_id=ingestion_id,
        received=len(batch.Records),
        accepted=accepted,
        rejected=rejected,
        duplicates=duplicates,
        events=results
    )

@router.post("/windows", response_model=IngestionStatus)
async def ingest_windows_sample(
    request: Request,
    source = Depends(verify_source),
    pipeline = Depends(get_pipeline),
    x_trace_id: Optional[str] = Header(None)
):
    if source.source_type.value != "windows_event":
        raise HTTPException(status_code=400, detail="Invalid source type for Windows ingestion")
        
    body = await request.body()
    if len(body) > MAX_PAYLOAD_SIZE:
        raise HTTPException(status_code=413, detail="Payload too large")
        
    status = await pipeline.process_event(
        payload=body.decode('utf-8'),
        source_id=str(source.id),
        source_name=source.name,
        source_type=source.source_type.value,
        content_type=request.headers.get("content-type", "application/json"),
        ingestion_method="http_windows_sample",
        ingestion_id=uuid.uuid4(),
        trace_id=x_trace_id,
        request_id=getattr(request.state, "request_id", None)
    )
    if status.status == "failed":
        raise HTTPException(status_code=503, detail=status.error)
    return status

@router.post("/kubernetes", response_model=IngestionStatus)
async def ingest_k8s_sample(
    request: Request,
    source = Depends(verify_source),
    pipeline = Depends(get_pipeline),
    x_trace_id: Optional[str] = Header(None)
):
    if source.source_type.value != "kubernetes_audit":
        raise HTTPException(status_code=400, detail="Invalid source type for K8s ingestion")
        
    body = await request.body()
    if len(body) > MAX_PAYLOAD_SIZE:
        raise HTTPException(status_code=413, detail="Payload too large")
        
    status = await pipeline.process_event(
        payload=body.decode('utf-8'),
        source_id=str(source.id),
        source_name=source.name,
        source_type=source.source_type.value,
        content_type=request.headers.get("content-type", "application/json"),
        ingestion_method="http_k8s_sample",
        ingestion_id=uuid.uuid4(),
        trace_id=x_trace_id,
        request_id=getattr(request.state, "request_id", None)
    )
    if status.status == "failed":
        raise HTTPException(status_code=503, detail=status.error)
    return status
