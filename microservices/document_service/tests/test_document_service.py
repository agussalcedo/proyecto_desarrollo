"""
Tests unitarios - DocumentService

DocumentService recibe un repositorio por constructor (Inyección de
Dependencias), así que para probar su lógica de negocio en aislamiento
usamos un repositorio falso en memoria en vez de conectar a MongoDB.
Esto es un test unitario real: rápido, sin I/O, y prueba solo la
responsabilidad de esta clase (principio de Responsabilidad Única).
"""
import pytest
from app.services.document_service import DocumentService


class FakeDocumentRepository:
    """
    Doble de prueba que cumple la misma interfaz que DocumentRepository,
    pero guarda todo en un diccionario en memoria.
    """

    def __init__(self):
        self._storage: dict[str, dict] = {}
        self._next_id = 1

    async def get_by_checksum(self, checksum: str):
        for doc in self._storage.values():
            if doc["checksum"] == checksum:
                return doc
        return None

    async def create(self, doc_data: dict) -> dict:
        doc_id = str(self._next_id)
        self._next_id += 1
        stored = {**doc_data, "id": doc_id}
        self._storage[doc_id] = stored
        return stored

    async def get_all(self, skip: int = 0, limit: int = 100):
        values = list(self._storage.values())
        return values[skip: skip + limit]

    async def get_by_id(self, doc_id: str):
        return self._storage.get(doc_id)

    async def update(self, doc_id: str, update_data: dict):
        if doc_id not in self._storage:
            return None
        self._storage[doc_id].update(update_data)
        return self._storage[doc_id]

    async def delete(self, doc_id: str) -> bool:
        return self._storage.pop(doc_id, None) is not None


@pytest.fixture
def service():
    return DocumentService(FakeDocumentRepository())


class TestProcessPdf:

    @pytest.mark.asyncio
    async def test_procesar_pdf_valido_lo_persiste(self, service, valid_pdf_bytes):
        resultado = await service.process_pdf(valid_pdf_bytes, "parcial.pdf")
        assert resultado["filename"] == "parcial.pdf"
        assert "Contenido de prueba" in resultado["content"]
        assert resultado["size_bytes"] == len(valid_pdf_bytes)
        assert "created_at" in resultado

    @pytest.mark.asyncio
    async def test_procesar_pdf_duplicado_lanza_error(self, service, valid_pdf_bytes):
        """Subir el mismo archivo dos veces debe rechazar la segunda vez."""
        await service.process_pdf(valid_pdf_bytes, "primero.pdf")
        with pytest.raises(ValueError, match="ya existe"):
            await service.process_pdf(valid_pdf_bytes, "segundo.pdf")

    @pytest.mark.asyncio
    async def test_procesar_pdf_invalido_lanza_error(self, service, invalid_pdf_bytes):
        with pytest.raises(ValueError):
            await service.process_pdf(invalid_pdf_bytes, "no_es_pdf.pdf")


class TestCrudBasico:

    @pytest.mark.asyncio
    async def test_get_all_devuelve_los_documentos_creados(self, service, valid_pdf_bytes):
        await service.process_pdf(valid_pdf_bytes, "uno.pdf")
        documentos = await service.get_all()
        assert len(documentos) == 1

    @pytest.mark.asyncio
    async def test_get_by_id_devuelve_none_si_no_existe(self, service):
        assert await service.get_by_id("no-existe") is None

    @pytest.mark.asyncio
    async def test_update_modifica_el_documento(self, service, valid_pdf_bytes):
        creado = await service.process_pdf(valid_pdf_bytes, "uno.pdf")
        actualizado = await service.update(creado["id"], {"content": "texto editado"})
        assert actualizado["content"] == "texto editado"

    @pytest.mark.asyncio
    async def test_delete_elimina_el_documento(self, service, valid_pdf_bytes):
        creado = await service.process_pdf(valid_pdf_bytes, "uno.pdf")
        assert await service.delete(creado["id"]) is True
        assert await service.get_by_id(creado["id"]) is None
