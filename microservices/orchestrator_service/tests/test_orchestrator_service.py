"""
Tests de OrchestratorService: cómo traduce los errores del cliente al
estado que informa el health check.
"""
import httpx
import pytest

from orchestrator_service.clients.resilience import CircuitOpenError
from orchestrator_service.services.orchestrator_service import OrchestratorService


class ClienteFalso:
    """Reemplaza al MicroserviceClient: siempre lanza el error indicado."""

    def __init__(self, error: Exception) -> None:
        self._error = error

    async def get(self, path: str, params=None):
        raise self._error


def _error_http(status: int) -> httpx.HTTPStatusError:
    return httpx.HTTPStatusError(
        "error",
        request=httpx.Request("GET", "http://servicio/health/ready"),
        response=httpx.Response(status),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error, esperado",
    [
        (CircuitOpenError(12.0), "circuit_open"),
        (_error_http(503), "not_ready"),
        (httpx.ConnectError("caído"), "unreachable"),
        (httpx.ReadTimeout("lento"), "unreachable"),
    ],
)
async def test_traduce_cada_error_a_un_estado(error, esperado):
    servicio = OrchestratorService()
    servicio._document_client = ClienteFalso(error)

    assert await servicio.check_document_service_health() == esperado
