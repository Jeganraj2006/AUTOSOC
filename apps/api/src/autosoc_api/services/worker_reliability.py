"""Durable retry bookkeeping shared by AutoSOC Kafka workers.

Kafka offsets are deliberately committed only after an operation has either
completed durably or has been written to the failed-event topic.  Redis holds
the retry counter so a worker restart cannot reset a poison message's budget.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from redis.asyncio import Redis

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetryDecision:
    """The next action for a failed Kafka message."""

    attempt: int
    delay_seconds: float
    exhausted: bool


class RedisRetryState:
    """Persist retry state by immutable Kafka message identity."""

    def __init__(
        self,
        redis_url: str,
        worker_name: str,
        *,
        max_attempts: int = 5,
        base_delay_seconds: float = 1.0,
        max_delay_seconds: float = 30.0,
        ttl_seconds: int = 86_400,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least one")
        self._redis = Redis.from_url(redis_url, decode_responses=True)
        self.worker_name = worker_name
        self.max_attempts = max_attempts
        self.base_delay_seconds = base_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.ttl_seconds = ttl_seconds

    @staticmethod
    def message_key(topic: str, partition: int, offset: int) -> str:
        return f"{topic}:{partition}:{offset}"

    def _key(self, message_key: str) -> str:
        return f"autosoc:worker-retry:{self.worker_name}:{message_key}"

    async def record_failure(self, message_key: str, error: Exception) -> RetryDecision:
        """Atomically increment the durable counter and return its retry plan."""
        key = self._key(message_key)
        attempt = int(await self._redis.hincrby(key, "attempt", 1))
        error_summary = f"{type(error).__name__}: {error}"[:1_000]
        await self._redis.hset(
            key,
            mapping={
                "last_error": error_summary,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        await self._redis.expire(key, self.ttl_seconds)
        exhausted = attempt >= self.max_attempts
        delay_seconds = min(
            self.max_delay_seconds,
            self.base_delay_seconds * (2 ** max(attempt - 1, 0)),
        )
        logger.warning(
            json.dumps(
                {
                    "event": "worker_retry_scheduled",
                    "worker": self.worker_name,
                    "message_key": message_key,
                    "attempt": attempt,
                    "max_attempts": self.max_attempts,
                    "delay_seconds": delay_seconds,
                    "exhausted": exhausted,
                    "error": error_summary,
                },
                sort_keys=True,
            )
        )
        return RetryDecision(attempt=attempt, delay_seconds=delay_seconds, exhausted=exhausted)

    async def acknowledge(self, message_key: str) -> None:
        await self._redis.delete(self._key(message_key))

    async def close(self) -> None:
        await self._redis.aclose()
