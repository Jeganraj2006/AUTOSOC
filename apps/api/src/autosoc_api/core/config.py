from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json
from pydantic import Field, computed_field, field_validator, model_validator
from pydantic_core import MultiHostUrl

class Settings(BaseSettings):
    PROJECT_NAME: str = "AutoSOC Backend API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    APP_VERSION: str = "0.1.0-dev"
    API_VERSION: str = "v1"
    API_V1_STR: str = "/api/v1"
    COMMIT_ID: str = "unknown"
    
    # Needs to be parsed from JSON string if set via env
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    
    # PostgreSQL Database Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    OPENSEARCH_HOSTS: str = "http://localhost:9200"
    REDPANDA_HOST: str = "localhost"
    REDPANDA_PORT: int = 19092
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OBJECT_STORAGE_HEALTH_URL: str = "http://localhost:9000"
    HEALTH_CHECK_TIMEOUT_SECONDS: float = Field(default=5.0, gt=0, le=10)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "autosoc"
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str = "auto_soc"
    POSTGRES_PORT: int = 5432
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Use sqlite for dev/tests if no postgres available
        if self.ENVIRONMENT == "test" or self.POSTGRES_SERVER == "sqlite":
            return "sqlite+aiosqlite:///./test.db"
        return str(MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        ))

    # Keycloak Configuration
    KEYCLOAK_SERVER_URL: str = "http://127.0.0.1:8080"
    KEYCLOAK_REALM: str = "autosoc"
    KEYCLOAK_CLIENT_ID: str = "autosoc-api"
    # This must match the audience claim issued by the configured Keycloak client.
    KEYCLOAK_AUDIENCE: str = Field(default="account", min_length=1)
    
    @computed_field
    @property
    def KEYCLOAK_JWKS_URL(self) -> str:
        return f"{self.KEYCLOAK_SERVER_URL}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/certs"

    @model_validator(mode="after")
    def require_database_credentials(self) -> "Settings":
        if (
            self.ENVIRONMENT != "test"
            and self.POSTGRES_SERVER != "sqlite"
            and not self.POSTGRES_PASSWORD
        ):
            raise ValueError("POSTGRES_PASSWORD is required when PostgreSQL is configured")
        return self

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str):
            try:
                return json.loads(v)
            except ValueError:
                return []
        return v

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
