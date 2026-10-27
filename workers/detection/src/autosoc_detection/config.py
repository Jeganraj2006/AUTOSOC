from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Kafka/Redpanda
    kafka_bootstrap_servers: str = "redpanda:9092"
    kafka_consumer_group: str = "autosoc-detection-worker"
    kafka_source_topic: str = "security.events.enriched"
    kafka_alert_topic: str = "security.alerts"
    
    # Redis for state management
    redis_url: str = "redis://redis:6379/1"
    retry_max_attempts: int = 5
    retry_base_delay_seconds: float = 1.0
    retry_max_delay_seconds: float = 30.0
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/autosoc"
    
    # Rules
    rules_dir: str = "/app/rules"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
