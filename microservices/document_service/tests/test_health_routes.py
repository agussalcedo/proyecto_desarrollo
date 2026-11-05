"""
Tests de los health checks del document_service.

Se reemplaza el ping a MongoDB por una función simulada, así que no
dependen de que Docker ni la base real estén levantados.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
import app.services.health_service as health_service_module


@pytest.fixture
def client():
    # Sin "with", TestClient no ejecuta el lifespan (que consultaría Mongo real).
    return TestClient(app)


def _simular_base_de_datos(monkeypatch, disponible: bool):
    async def ping_falso() -> bool:
        return disponible

    monkeypatch.setattr(health_service_module, "ping_database", ping_falso)


class TestLiveness:

    def test_live_responde_200_sin_consultar_dependencias(self, client, monkeypatch):
        _simular_base_de_datos(monkeypatch, disponible=False)

        response = client.get("/health/live")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "alive"
        assert body["uptime_seconds"] >= 0


class TestReadiness:

    def test_ready_responde_200_si_la_base_esta_disponible(self, client, monkeypatch):
        _simular_base_de_datos(monkeypatch, disponible=True)

        response = client.get("/health/ready")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ready"
        assert body["checks"] == {"database": "up"}

    def test_ready_responde_503_si_la_base_no_responde(self, client, monkeypatch):
        _simular_base_de_datos(monkeypatch, disponible=False)

        response = client.get("/health/ready")

        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "not_ready"
        assert body["checks"] == {"database": "down"}

    def test_health_es_alias_de_ready(self, client, monkeypatch):
        _simular_base_de_datos(monkeypatch, disponible=False)

        assert client.get("/health").status_code == 503

        _simular_base_de_datos(monkeypatch, disponible=True)

        assert client.get("/health").status_code == 200
