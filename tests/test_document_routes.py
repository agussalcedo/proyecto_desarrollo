"""
Tests de sistema (end-to-end) - endpoints de /documents

Prueban la aplicación completa a través de la capa HTTP: rutas ->
servicio -> repositorio -> base de datos. Se usa mongomock-motor en
vez de una base real para que la suite corra igual en cualquier
compu del equipo, sin depender de que Docker esté levantado.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient

from app.main import app
import app.routes.document_routes as document_routes_module


@pytest.fixture(autouse=True)
def usar_base_de_datos_simulada(monkeypatch):
    """
    Reemplaza la base de datos real por una simulada en memoria antes
    de cada test, así los tests de sistema no dependen de Mongo real.
    """
    client = AsyncMongoMockClient()
    fake_database = client["test_database"]
    monkeypatch.setattr(document_routes_module, "database", fake_database)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _pdf_file(pdf_bytes: bytes, filename: str = "parcial.pdf"):
    return {"file": (filename, pdf_bytes, "application/pdf")}


class TestUploadDocument:

    @pytest.mark.asyncio
    async def test_subir_pdf_valido_devuelve_201(self, client, valid_pdf_bytes):
        response = await client.post("/documents/upload", files=_pdf_file(valid_pdf_bytes))
        assert response.status_code == 201
        body = response.json()
        assert body["filename"] == "parcial.pdf"
        assert "id" in body

    @pytest.mark.asyncio
    async def test_subir_archivo_sin_extension_pdf_devuelve_400(self, client, valid_pdf_bytes):
        response = await client.post("/documents/upload", files=_pdf_file(valid_pdf_bytes, "foto.png"))
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_subir_archivo_que_no_es_pdf_real_devuelve_400(self, client, invalid_pdf_bytes):
        response = await client.post("/documents/upload", files=_pdf_file(invalid_pdf_bytes))
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_subir_el_mismo_pdf_dos_veces_devuelve_400_la_segunda(self, client, valid_pdf_bytes):
        await client.post("/documents/upload", files=_pdf_file(valid_pdf_bytes))
        response = await client.post("/documents/upload", files=_pdf_file(valid_pdf_bytes))
        assert response.status_code == 400
        assert "ya existe" in response.json()["detail"]


class TestGetDocuments:

    @pytest.mark.asyncio
    async def test_listar_documentos_vacio_al_inicio(self, client):
        response = await client.get("/documents/")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_obtener_documento_por_id(self, client, valid_pdf_bytes):
        subida = await client.post("/documents/upload", files=_pdf_file(valid_pdf_bytes))
        doc_id = subida.json()["id"]

        response = await client.get(f"/documents/{doc_id}")
        assert response.status_code == 200
        assert response.json()["id"] == doc_id

    @pytest.mark.asyncio
    async def test_obtener_documento_con_id_mal_formado_devuelve_400(self, client):
        response = await client.get("/documents/id-invalido")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_obtener_documento_inexistente_devuelve_404(self, client):
        from bson import ObjectId
        response = await client.get(f"/documents/{ObjectId()}")
        assert response.status_code == 404


class TestUpdateDocument:

    @pytest.mark.asyncio
    async def test_actualizar_documento_existente(self, client, valid_pdf_bytes):
        subida = await client.post("/documents/upload", files=_pdf_file(valid_pdf_bytes))
        doc_id = subida.json()["id"]

        response = await client.put(f"/documents/{doc_id}", json={"content": "texto editado"})
        assert response.status_code == 200
        assert response.json()["content"] == "texto editado"

    @pytest.mark.asyncio
    async def test_actualizar_documento_inexistente_devuelve_404(self, client):
        from bson import ObjectId
        response = await client.put(f"/documents/{ObjectId()}", json={"content": "no importa"})
        assert response.status_code == 404


class TestDeleteDocument:

    @pytest.mark.asyncio
    async def test_eliminar_documento_existente_devuelve_204(self, client, valid_pdf_bytes):
        subida = await client.post("/documents/upload", files=_pdf_file(valid_pdf_bytes))
        doc_id = subida.json()["id"]

        response = await client.delete(f"/documents/{doc_id}")
        assert response.status_code == 204

        seguimiento = await client.get(f"/documents/{doc_id}")
        assert seguimiento.status_code == 404

    @pytest.mark.asyncio
    async def test_eliminar_documento_inexistente_devuelve_404(self):
        from bson import ObjectId
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.delete(f"/documents/{ObjectId()}")
            assert response.status_code == 404


class TestHealthEndpoints:

    @pytest.mark.asyncio
    async def test_root_devuelve_estado_online(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "online"

    @pytest.mark.asyncio
    async def test_health_devuelve_healthy(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
