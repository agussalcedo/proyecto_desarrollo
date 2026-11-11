"""
Lógica de negocio - Business Layer
"""
import logging
from functools import lru_cache

import httpx

from orchestrator_service.clients.microservice_client import MicroserviceClient
from orchestrator_service.clients.resilience import CircuitBreaker, CircuitOpenError
from orchestrator_service.core.config import settings

logger = logging.getLogger(__name__)


class OrchestratorService:
    """
    Orquesta llamadas a los distintos microservicios del sistema.
    No persiste datos: delega esa responsabilidad en cada microservicio.
    """

    def __init__(self) -> None:
        self._document_client = MicroserviceClient(
            base_url=settings.DOCUMENT_SERVICE_URL,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
            connect_timeout=settings.CONNECT_TIMEOUT_SECONDS,
            max_attempts=settings.RETRY_MAX_ATTEMPTS,
            backoff_seconds=settings.RETRY_BACKOFF_SECONDS,
            breaker=CircuitBreaker(
                failure_threshold=settings.CIRCUIT_FAILURE_THRESHOLD,
                recovery_timeout=settings.CIRCUIT_RECOVERY_SECONDS,
            ),
        )

    async def check_document_service_health(self) -> str:
        """
        Consulta el readiness del microservicio de documentos.

        Devuelve:
          - "ready":        responde y sus dependencias están bien
          - "not_ready":    responde, pero informa que no puede atender pedidos (503)
          - "unreachable":  no se pudo conectar (caído, timeout, red)
          - "circuit_open": el Circuit Breaker está abierto; ni siquiera se intentó
        """
        try:
            data = await self._document_client.get("/health/ready")
            return data.get("status", "unknown")
        except CircuitOpenError as error:
            logger.warning("document_service: circuito abierto (%s)", error)
            return "circuit_open"
        except httpx.HTTPStatusError as error:
            logger.warning("document_service no está listo: HTTP %s", error.response.status_code)
            return "not_ready"
        except httpx.HTTPError as error:
            logger.warning("document_service inalcanzable: %s", error.__class__.__name__)
            return "unreachable"


@lru_cache(maxsize=1)
def get_orchestrator_service() -> OrchestratorService:
    """
    Instancia única compartida por todas las rutas. Es importante que sea una
    sola: el Circuit Breaker guarda el estado del servicio remoto, y si cada
    ruta tuviera su propia instancia no compartirían lo que van aprendiendo.
    """
    return OrchestratorService()
