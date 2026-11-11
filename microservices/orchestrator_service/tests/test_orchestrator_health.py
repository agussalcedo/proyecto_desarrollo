"""
Tests de los health checks del orchestrator_service.

Se simula la respuesta del document_service, así que no dependen de
que Docker ni los otros microservicios estén levantados.
"""
import pytest
from fastapi.testclient import TestClient

from orchestrator_service.main import app
from orchestrator_service.services.orchestrator_service import OrchestratorService


@pytest.fixture
def client():
    return TestClient(app)


def _simular_document_service(monkeypatch, estado: str):
    async def estado_falso(self) -> str:
        return estado

    monkeypatch.setattr(OrchestratorService, "check_document_service_health", estado_falso)


class TestLiveness:

    def test_live_responde_200_sin_consultar_dependencias(self, client, monkeypatch):
        _simular_document_service(monkeypatch, "unreachable")

        response = client.get("/orchestrator/health/live")

        assert response.status_code == 200
        assert response.json()["status"] == "alive"


class TestReadiness:

    def test_ready_responde_200_si_document_service_esta_listo(self, client, monkeypatch):
        _simular_document_service(monkeypatch, "ready")

        response = client.get("/orchestrator/health/ready")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ready"
        assert body["checks"] == {"document_service": "ready"}

    @pytest.mark.parametrize("estado", ["not_ready", "unreachable"])
    def test_ready_responde_503_si_document_service_falla(self, client, monkeypatch, estado):
        _simular_document_service(monkeypatch, estado)

        response = client.get("/orchestrator/health/ready")

        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "not_ready"
        assert body["checks"] == {"document_service": estado}


class TestStatus:

    def test_status_informa_el_estado_de_la_dependencia(self, client, monkeypatch):
        _simular_document_service(monkeypatch, "unreachable")

        response = client.get("/orchestrator/status")

        assert response.status_code == 200
        assert response.json()["dependencies"] == [
            {"service": "document_service", "status": "unreachable"}
        ]
