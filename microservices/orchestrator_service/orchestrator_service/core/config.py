"""
Configuración - Orchestrator Service
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Orchestrator Service"
    APP_VERSION: str = "0.1.0"
    # Por defecto apunta al nombre del servicio dentro de la red de Docker Compose.
    DOCUMENT_SERVICE_URL: str = "http://document_service:8000"
    # Timeouts hacia el document_service. El de conexión es más corto que el de
    # lectura: si el servicio no atiende, es mejor enterarse en 2 s que en 5 s.
    CONNECT_TIMEOUT_SECONDS: float = 2.0
    REQUEST_TIMEOUT_SECONDS: float = 5.0

    # Retry: cantidad total de intentos (1 = sin reintentos) y espera base entre ellos.
    RETRY_MAX_ATTEMPTS: int = 3
    RETRY_BACKOFF_SECONDS: float = 0.2

    # Circuit Breaker: fallos seguidos para abrir y segundos antes de volver a probar.
    CIRCUIT_FAILURE_THRESHOLD: int = 5
    CIRCUIT_RECOVERY_SECONDS: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
