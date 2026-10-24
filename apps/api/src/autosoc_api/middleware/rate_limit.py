import time
import asyncio
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Basic in-memory rate limiter for academic/dev demonstration
# In production, use Redis.
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit: int = 100, window: int = 60):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window = window
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Only rate limit specific sensitive paths for SOC
        sensitive_paths = ["/responses", "/agents", "/incidents"]
        
        path = request.url.path
        if any(sp in path for sp in sensitive_paths) and request.method in ["POST", "PUT", "DELETE"]:
            client_ip = request.client.host
            now = time.time()
            
            # Clean up old requests
            self.requests[client_ip] = [req_time for req_time in self.requests[client_ip] if now - req_time < self.window]
            
            if len(self.requests[client_ip]) >= self.rate_limit:
                logger.warning(f"Rate limit exceeded for IP {client_ip} on path {path}")
                return JSONResponse(
                    status_code=429,
                    content={"error_code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests. Please try again later."}
                )
            
            self.requests[client_ip].append(now)

        return await call_next(request)
