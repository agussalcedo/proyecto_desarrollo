from typing import List
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from app.core.database import database
from app.core.config import settings
from app.schemas.document_schema import DocumentResponse, DocumentUpdate
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService

# Definicion del router con su prefijo y etiquetas para Swagger
router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """
    Endpoint para subir un PDF, extraer texto y persistirlo.
    Incluye validaciones de formato, tamano y contenido.
    """
    # 1. Validacion de extension por nombre de archivo
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La extension del archivo debe ser .pdf"
        )

    # 2. Validacion de Content-Type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El tipo de archivo debe ser application/pdf"
        )

    # 3. Leer contenido en memoria (Requisito: Sin persistencia temporal)
    file_content = await file.read()
    
    # 4. Validacion de tamano (15MB definidos en settings)
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El archivo supera el limite permitido de 15MB"
        )

    # 5. Validacion de Seguridad: Magic Bytes
    if not file_content.startswith(b'%PDF'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El contenido del archivo no es un PDF valido"
        )

    # Instanciacion de capas de persistencia y negocio
    repo = DocumentRepository(database)
    service = DocumentService(repo)
    
    try:
        # El servicio gestiona Checksum, Extraccion y Persistencia
        return await service.process_pdf(file_content, file.filename)
    except ValueError as e:
        # Captura errores de duplicados (checksum) o errores de proceso
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Internal Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error interno al procesar el documento"
        )

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(skip: int = 0, limit: int = 100):
    """CRUD: Obtener lista de documentos persistidos"""
    repo = DocumentRepository(database)
    service = DocumentService(repo)
    return await service.get_all(skip, limit)

@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: str):
    """CRUD: Eliminar un documento por su ID unico"""
    repo = DocumentRepository(database)
    service = DocumentService(repo)
    if not await service.delete(doc_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Documento no encontrado"
        )