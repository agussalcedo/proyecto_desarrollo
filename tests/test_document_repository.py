"""
Tests de integración - DocumentRepository

A diferencia de los tests unitarios de DocumentService (que usan un
repositorio falso), estos tests prueban que DocumentRepository arma
correctamente las consultas contra una base MongoDB real, usando
mongomock-motor para simular el motor de Mongo sin necesitar un
servidor real corriendo.
"""
import pytest
from mongomock_motor import AsyncMongoMockClient
from app.repositories.document_repository import DocumentRepository


@pytest.fixture
def repository():
    client = AsyncMongoMockClient()
    database = client["test_database"]
    return DocumentRepository(database)


@pytest.fixture
def sample_doc() -> dict:
    return {
        "filename": "ejemplo.pdf",
        "content": "contenido de ejemplo",
        "checksum": "abc123",
        "size_bytes": 1024,
    }


class TestCreateAndRetrieve:

    @pytest.mark.asyncio
    async def test_create_persiste_y_devuelve_id(self, repository, sample_doc):
        creado = await repository.create(sample_doc)
        assert "id" in creado
        assert creado["filename"] == "ejemplo.pdf"

    @pytest.mark.asyncio
    async def test_get_by_id_encuentra_el_documento_creado(self, repository, sample_doc):
        creado = await repository.create(sample_doc)
        encontrado = await repository.get_by_id(creado["id"])
        assert encontrado["filename"] == "ejemplo.pdf"

    @pytest.mark.asyncio
    async def test_get_by_checksum_encuentra_duplicados(self, repository, sample_doc):
        await repository.create(sample_doc)
        encontrado = await repository.get_by_checksum("abc123")
        assert encontrado is not None

    @pytest.mark.asyncio
    async def test_get_by_checksum_devuelve_none_si_no_existe(self, repository):
        assert await repository.get_by_checksum("no-existe") is None

    @pytest.mark.asyncio
    async def test_get_all_respeta_skip_y_limit(self, repository, sample_doc):
        for i in range(5):
            await repository.create({**sample_doc, "checksum": f"hash-{i}"})
        pagina = await repository.get_all(skip=2, limit=2)
        assert len(pagina) == 2


class TestUpdateAndDelete:

    @pytest.mark.asyncio
    async def test_update_modifica_campos_existentes(self, repository, sample_doc):
        creado = await repository.create(sample_doc)
        actualizado = await repository.update(creado["id"], {"content": "editado"})
        assert actualizado["content"] == "editado"

    @pytest.mark.asyncio
    async def test_delete_elimina_y_devuelve_true(self, repository, sample_doc):
        creado = await repository.create(sample_doc)
        assert await repository.delete(creado["id"]) is True
        assert await repository.get_by_id(creado["id"]) is None

    @pytest.mark.asyncio
    async def test_delete_de_id_inexistente_devuelve_false(self, repository):
        from bson import ObjectId
        assert await repository.delete(str(ObjectId())) is False
