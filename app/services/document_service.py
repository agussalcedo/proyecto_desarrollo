import hashlib
import io
import fitz  # PyMuPDF (Instalalo con: uv add pymupdf)
from typing import Optional, List
from app.repositories.document_repository import DocumentRepository

class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    async def process_pdf(self, file_bytes: bytes, filename: str) -> dict:
        """
        Lógica central: Extrae texto, calcula checksum y persiste.
        """
        # 1. Calcular Checksum (Suma de verificación)
        checksum = hashlib.sha256(file_bytes).hexdigest()

        # 2. Validar duplicados por checksum 
        if await self.repository.get_by_checksum(checksum):
            raise ValueError("El documento ya existe (duplicado por checksum)")

        # 3. Extraer texto solamente (Sin archivos temporales)
        text_content = ""
        try:
            # Abrimos el stream de bytes directamente en memoria 
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for page in doc:
                    text_content += page.get_text()
        except Exception as e:
            raise ValueError(f"Error técnico al extraer texto del PDF: {str(e)}")

        # 4. Estructurar datos para persistir en DB No Relacional
        doc_dict = {
            "filename": filename,
            "content": text_content,
            "checksum": checksum,
            "size_bytes": len(file_bytes)
        }
        
        return await self.repository.create(doc_dict)

    async def get_all(self, skip: int = 0, limit: int = 100):
        """CRUD: Obtener documentos persistidos"""
        return await self.repository.get_all(skip, limit)

    async def delete(self, doc_id: str):
        """CRUD: Eliminar un documento"""
        return await self.repository.delete(doc_id)