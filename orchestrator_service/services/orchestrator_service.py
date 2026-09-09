"""
Lógica de negocio - Business Layer
"""
from orchestrator_service.clients.microservice_client import MicroserviceClient
from orchestrator_service.core.config import settings


class OrchestratorService:
    """
    Orquesta llamadas a los distintos microservicios del sistema.
    No persiste datos: delega esa responsabilidad en cada microservicio.
    """

    def __init__(self) -> None:
        self._document_client = MicroserviceClient(
            base_url=settings.DOCUMENT_SERVICE_URL,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        )

    async def check_document_service_health(self) -> dict:
        """Verifica que el microservicio de documentos esté disponible."""
        return await self._document_client.get("/health")
