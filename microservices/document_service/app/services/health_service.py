"""
Lógica de negocio - Health checks
"""
import time

from app.core.config import settings
from app.core.database import ping_database
from app.schemas.health_schema import LivenessResponse, ReadinessResponse


class HealthService:
    """
    Distingue dos preguntas distintas:
      - liveness:  ¿el proceso está vivo? (no mira dependencias)
      - readiness: ¿puede atender pedidos ahora? (verifica MongoDB)
    """

    def __init__(self) -> None:
        self._started_at = time.monotonic()

    def liveness(self) -> LivenessResponse:
        return LivenessResponse(
            status="alive",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            uptime_seconds=int(time.monotonic() - self._started_at),
        )

    async def readiness(self) -> ReadinessResponse:
        database_up = await ping_database()
        return ReadinessResponse(
            status="ready" if database_up else "not_ready",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            checks={"database": "up" if database_up else "down"},
        )
