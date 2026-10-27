import redis
import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class RedisStateManager:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.ttl = 86400  # Default TTL: 24 hours

    @classmethod
    def from_url(cls, redis_url: str) -> "RedisStateManager":
        parsed = urlparse(redis_url)
        return cls(
            host=parsed.hostname or "localhost",
            port=parsed.port or 6379,
            db=int((parsed.path or "/0").lstrip("/") or 0),
        )
        
    def _generate_key(self, entity_id: str, rule_id: str) -> str:
        return f"corr:{rule_id}:{entity_id}"
        
    def add_alert(self, entity_id: str, rule_id: str, alert_data: Dict[str, Any], window_seconds: int):
        key = self._generate_key(entity_id, rule_id)
        # Use a sorted set to keep alerts ordered by timestamp
        timestamp = alert_data.get("detected_at") or alert_data.get("timestamp")
        
        # If timestamp is a string (e.g., ISO format), parse it or just use current time as score
        try:
            if isinstance(timestamp, str):
                score = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).timestamp()
            else:
                score = datetime.now().timestamp()
        except Exception:
            score = datetime.now().timestamp()
            
        alert_json = json.dumps(alert_data)
        
        # Add to sorted set
        self.redis.zadd(key, {alert_json: score})
        
        # Remove old alerts outside the window
        min_score = score - window_seconds
        self.redis.zremrangebyscore(key, "-inf", min_score)
        
        # Reset TTL for the key
        self.redis.expire(key, self.ttl)
        
    def get_alerts(self, entity_id: str, rule_id: str) -> List[Dict[str, Any]]:
        key = self._generate_key(entity_id, rule_id)
        alerts_json = self.redis.zrange(key, 0, -1)
        return [json.loads(aj) for aj in alerts_json]

    def clear_alerts(self, entity_id: str, rule_id: str):
        key = self._generate_key(entity_id, rule_id)
        self.redis.delete(key)
        
    def set_active_incident(self, entity_id: str, rule_id: str, incident_id: str):
        key = f"active_inc:{rule_id}:{entity_id}"
        self.redis.setex(key, self.ttl, incident_id)
        
    def get_active_incident(self, entity_id: str, rule_id: str) -> Optional[str]:
        key = f"active_inc:{rule_id}:{entity_id}"
        return self.redis.get(key)
        
    def clear_active_incident(self, entity_id: str, rule_id: str):
        key = f"active_inc:{rule_id}:{entity_id}"
        self.redis.delete(key)

# Docker workers must use the Compose DNS name rather than their own localhost.
state_manager = RedisStateManager.from_url(
    os.environ.get("REDIS_URL", "redis://redis:6379/2")
)
