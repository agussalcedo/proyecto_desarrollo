from typing import List
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from bson.errors import InvalidId
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
    # 1. Validacion de extension usando la lista configurada en settings
    extension = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La extension del archivo debe ser: {', '.join(settings.ALLOWED_EXTENSIONS)}"
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

@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str):
    """CRUD: Obtener un documento individual por su ID"""
    repo = DocumentRepository(database)
    service = DocumentService(repo)
    try:
        document = await service.get_by_id(doc_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no tiene un formato valido"
        )
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    return document

@router.put("/{doc_id}", response_model=DocumentResponse)
async def update_document(doc_id: str, update_data: DocumentUpdate):
    """CRUD: Actualizar el contenido de un documento existente"""
    repo = DocumentRepository(database)
    service = DocumentService(repo)
    try:
        updated = await service.update(doc_id, update_data.model_dump(exclude_none=True))
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no tiene un formato valido"
        )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    return updated

@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: str):
    """CRUD: Eliminar un documento por su ID unico"""
    repo = DocumentRepository(database)
    service = DocumentService(repo)
    try:
        deleted = await service.delete(doc_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no tiene un formato valido"
        )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Documento no encontrado"
        )