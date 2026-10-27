from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = "redpanda:9092"
    INCIDENTS_TOPIC: str = "security.incidents"
    PREDICTIONS_TOPIC: str = "security.predictions"
    FAILED_TOPIC: str = "security.events.failed"
    REDIS_URL: str = "redis://redis:6379/3"
    RETRY_MAX_ATTEMPTS: int = 5
    RETRY_BASE_DELAY_SECONDS: float = 1.0
    RETRY_MAX_DELAY_SECONDS: float = 30.0
    DATABASE_URL: str = "postgresql+asyncpg://autosoc_user:autosoc_password@postgres:5432/autosoc"
    MODEL_PATH: str = "/app/models/markov_model.json"
    VOCAB_PATH: str = "/app/models/vocab.json"
    
    class Config:
        env_file = ".env"

settings = Settings()
