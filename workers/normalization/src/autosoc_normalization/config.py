from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    REDPANDA_BROKERS: str = "localhost:9092"
    CONSUMER_GROUP: str = "autosoc-normalization-group"
    TOPIC_RAW: str = "security.events.raw"
    TOPIC_NORMALIZED: str = "security.events.normalized"
    TOPIC_ENRICHED: str = "security.events.enriched"
    TOPIC_FAILED: str = "security.events.failed"
    REDIS_URL: str = "redis://redis:6379/0"
    RETRY_MAX_ATTEMPTS: int = 5
    RETRY_BASE_DELAY_SECONDS: float = 1.0
    RETRY_MAX_DELAY_SECONDS: float = 30.0
    OPENSEARCH_HOSTS: str = "http://localhost:9200"
    LOG_LEVEL: str = "INFO"

settings = Settings()
