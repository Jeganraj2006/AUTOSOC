from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = "redpanda:9092"
    INCIDENTS_TOPIC: str = "security.incidents"
    PREDICTIONS_TOPIC: str = "security.predictions"
    DATABASE_URL: str = "postgresql+asyncpg://autosoc_user:autosoc_password@postgres:5432/autosoc"
    MODEL_PATH: str = "/app/models/markov_model.json"
    VOCAB_PATH: str = "/app/models/vocab.json"
    
    class Config:
        env_file = ".env"

settings = Settings()
