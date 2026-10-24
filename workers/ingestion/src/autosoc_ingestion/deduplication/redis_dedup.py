import logging
import asyncio
import redis.asyncio as redis
from typing import Optional

logger = logging.getLogger("ingestion.deduplication.redis")

class DeduplicationService:
    def __init__(self, redis_url: str, ttl_seconds: int = 3600):
        self.redis_url = redis_url
        self.ttl_seconds = ttl_seconds
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        try:
            # Note: For tests, if redis_url is empty, we could fallback to an in-memory dict,
            # but to adhere to the Phase 6 MVP, we'll configure Redis directly or mock it in pytest.
            self.client = redis.from_url(self.redis_url)
            await self.client.ping()
            logger.info("Connected to Redis for deduplication")
        except Exception as e:
            logger.error(f"Failed to connect to Redis at {self.redis_url}: {e}")
            self.client = None

    async def disconnect(self):
        if self.client:
            await self.client.aclose()
            logger.info("Disconnected from Redis")

    async def is_duplicate(self, source_id: str, payload_hash: str) -> bool:
        """
        Checks if an event is a duplicate within the TTL window.
        Returns True if duplicate, False if unique.
        """
        if not self.client:
            logger.warning("Redis client not initialized, bypassing deduplication check (failing open)")
            return False
            
        key = f"dedup:{source_id}:{payload_hash}"
        try:
            # SETNX (set if not exists) is atomic
            is_new = await self.client.set(key, "1", ex=self.ttl_seconds, nx=True)
            # is_new is True if the key was set, meaning it's unique
            return not bool(is_new)
        except Exception as e:
            logger.error(f"Redis error during deduplication check: {e}")
            # Fail open: if redis is down, assume not duplicate to prevent silent event loss
            return False
