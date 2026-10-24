import os
import uuid
import time
from typing import Callable, Any, Awaitable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from fastapi.responses import JSONResponse

from autosoc_api.core.config import settings
from autosoc_api.core.logging import setup_logging, get_logger
from autosoc_api.api.v1.router import api_router

# Initialize logging
setup_logging(log_level=settings.LOG_LEVEL)
logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

# Rate Limiting Middleware
from autosoc_api.middleware.rate_limit import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware, rate_limit=50, window=60)

# Request ID Middleware
@app.middleware("http")
async def add_request_id_and_log(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    request_id = request.headers.get("X-Request-ID")
    if not request_id or len(request_id) > 50 or not request_id.isalnum():
        request_id = str(uuid.uuid4())
    
    # Store request_id in request state
    request.state.request_id = request_id
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled Exception: {exc}", extra={"request_id": request_id})
        # Note: Do not return stack trace to client
        response = JSONResponse(
            status_code=500,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "request_id": request_id,
            }
        )
        
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Validation Error Handler
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Input validation failed.",
            "details": exc.errors(),
            "request_id": request_id,
        },
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": settings.PROJECT_NAME,
        "api_version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "phase": "Phase 5 - Core Backend",
        "docs_url": "/docs"
    }
