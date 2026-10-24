import asyncio
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from autosoc_detection.config import settings
import redis.asyncio as redis

logger = logging.getLogger(__name__)
app = FastAPI(title="Detection Worker Health API")

@app.get("/health/live")
async def liveness():
    return {"status": "ok", "service": "detection_worker"}

@app.get("/health/ready")
async def readiness():
    # Check Redis
    redis_ok = False
    try:
        r = redis.from_url(settings.redis_url)
        await r.ping()
        await r.aclose()
        redis_ok = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        
    if not redis_ok:
        return JSONResponse(status_code=503, content={"status": "error", "redis": "down"})
        
    return {"status": "ok", "redis": "up", "redpanda": "assumed_up"}

async def start_health_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()
