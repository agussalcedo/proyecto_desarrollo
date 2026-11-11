"""
Lógica de negocio - Health checks del orquestador
"""
import time
from typing import Optional

from orchestrator_service.core.config import settings
from orchestrator_service.schemas.orchestrator_schema import LivenessResponse, ReadinessResponse
from orchestrator_service.services.orchestrator_service import (
    OrchestratorService,
    get_orchestrator_service,
)


class HealthService:
    """
    Distingue dos preguntas distintas:
      - liveness:  ¿el proceso está vivo? (no mira dependencias)
      - readiness: ¿puede atender pedidos ahora? (verifica el document_service)
    """

    def __init__(self, orchestrator: Optional[OrchestratorService] = None) -> None:
        self._orchestrator = orchestrator or get_orchestrator_service()
        self._started_at = time.monotonic()

    def liveness(self) -> LivenessResponse:
        return LivenessResponse(
            status="alive",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            uptime_seconds=int(time.monotonic() - self._started_at),
        )

    async def readiness(self) -> ReadinessResponse:
        document_service_status = await self._orchestrator.check_document_service_health()
        return ReadinessResponse(
            status="ready" if document_service_status == "ready" else "not_ready",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
            checks={"document_service": document_service_status},
        )
