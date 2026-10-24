import time
import logging
import redis.asyncio as redis
from typing import Optional
from fastapi import HTTPException

logger = logging.getLogger("ingestion.rate_limiter")

class RateLimiterService:
    def __init__(self, redis_url: str, limit_per_minute: int = 600):
        self.redis_url = redis_url
        self.limit = limit_per_minute
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        try:
            self.client = redis.from_url(self.redis_url)
            await self.client.ping()
        except Exception as e:
            logger.error(f"Rate Limiter Redis connection failed: {e}")
            self.client = None

    async def check_rate_limit(self, source_id: str):
        if not self.client:
            # Fail open if Redis is down
            return
            
        current_minute = int(time.time() / 60)
        key = f"rate_limit:{source_id}:{current_minute}"
        
        try:
            # Atomic increment
            count = await self.client.incr(key)
            if count == 1:
                await self.client.expire(key, 120) # Expire after 2 mins
                
            if count > self.limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiter failure: {e}")
            # Fail open for safety
            pass
