from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Redpanda
    REDPANDA_BROKERS: str = "localhost:9092"
    REDPANDA_RAW_TOPIC: str = "security.events.raw"
    REDPANDA_FAILED_TOPIC: str = "security.events.failed"
    
    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "autosoc-raw-events"
    MINIO_SECURE: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    DEDUP_TTL_SECONDS: int = 3600
    RATE_LIMIT_PER_MINUTE: int = 600
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
