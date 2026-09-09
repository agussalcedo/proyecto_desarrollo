from typing import Optional, List
from app.repositories.document_repository import DocumentRepository
from app.services.pdf_processor import extract_text, calculate_checksum
from app.models.document_model import Document

class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    async def process_pdf(self, file_bytes: bytes, filename: str) -> dict:
        """
        Lógica central: Extrae texto, calcula checksum y persiste.
        """
        # 1. Calcular Checksum (Suma de verificación) usando pdf_processor
        checksum = calculate_checksum(file_bytes)

        # 2. Validar duplicados por checksum
        if await self.repository.get_by_checksum(checksum):
            raise ValueError("El documento ya existe (duplicado por checksum)")

        # 3. Extraer texto usando pdf_processor (sin duplicar lógica)
        try:
            text_content = extract_text(file_bytes)
        except ValueError as e:
            raise ValueError(f"Error técnico al extraer texto del PDF: {str(e)}")

        # 4. Construir el documento con el modelo Pydantic (incluye created_at automático)
        document = Document(
            filename=filename,
            content=text_content,
            checksum=checksum,
            size_bytes=len(file_bytes),
        )

        return await self.repository.create(document.model_dump())

    async def get_all(self, skip: int = 0, limit: int = 100):
        """CRUD: Obtener documentos persistidos"""
        return await self.repository.get_all(skip, limit)

    async def get_by_id(self, doc_id: str) -> Optional[dict]:
        """CRUD: Obtener un documento individual por su ID"""
        return await self.repository.get_by_id(doc_id)

    async def update(self, doc_id: str, update_data: dict) -> Optional[dict]:
        """CRUD: Actualizar un documento existente"""
        return await self.repository.update(doc_id, update_data)

    async def delete(self, doc_id: str):
        """CRUD: Eliminar un documento"""
        return await self.repository.delete(doc_id)