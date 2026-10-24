import redis.asyncio as redis
import time
from typing import Optional

class StateManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def close(self):
        await self.redis.aclose()

    async def increment_and_check_threshold(self, rule_id: str, group_key: str, limit: int, window: int) -> bool:
        """
        Increments a counter for a rule+group_key within a sliding window.
        Returns True if threshold is crossed exactly on this increment.
        """
        key = f"autosoc:detect:count:{rule_id}:{group_key}"
        
        # Simple sliding window counter using Redis
        current_time = int(time.time())
        window_start = current_time - window
        
        # Remove old events outside the window
        await self.redis.zremrangebyscore(key, "-inf", window_start)
        
        # Add new event (score is timestamp, value is timestamp + random tiebreaker to keep unique)
        event_val = f"{current_time}:{time.time_ns()}"
        await self.redis.zadd(key, {event_val: current_time})
        
        # Count elements in window
        count = await self.redis.zcard(key)
        
        # Set TTL on key to avoid indefinite memory usage
        await self.redis.expire(key, window)
        
        # Match only when exactly crossing the threshold to avoid storms
        # Suppressions will handle subsequent alerts
        return count >= limit

    async def is_suppressed(self, rule_id: str, group_key: str) -> bool:
        """Check if an alert for this rule+group is currently suppressed."""
        key = f"autosoc:detect:suppress:{rule_id}:{group_key}"
        return await self.redis.exists(key) > 0

    async def set_suppression(self, rule_id: str, group_key: str, ttl: int):
        """Set a suppression lock."""
        if ttl > 0:
            key = f"autosoc:detect:suppress:{rule_id}:{group_key}"
            await self.redis.set(key, "1", ex=ttl)

    async def check_is_new_value(self, category: str, value: str, ttl: int) -> bool:
        """
        Used for statistical/stateful detections (e.g. newly observed IP).
        Returns True if the value has NOT been seen before within the TTL window.
        """
        key = f"autosoc:detect:seen:{category}:{value}"
        # Setnx returns 1 if key was set (new), 0 if it already existed
        is_new = await self.redis.set(key, "1", nx=True, ex=ttl)
        return bool(is_new)
