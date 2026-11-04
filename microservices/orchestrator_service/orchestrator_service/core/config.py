"""
Configuración - Orchestrator Service
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Orchestrator Service"
    APP_VERSION: str = "0.1.0"
    # Por defecto apunta al nombre del servicio dentro de la red de Docker Compose.
    DOCUMENT_SERVICE_URL: str = "http://document_service:8000"
    REQUEST_TIMEOUT_SECONDS: float = 5.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
