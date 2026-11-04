"""
Configuración - Orchestrator Service
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Orchestrator Service"
    APP_VERSION: str = "0.1.0"
    DOCUMENT_SERVICE_URL: str
    REQUEST_TIMEOUT_SECONDS: float = 5.0

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()