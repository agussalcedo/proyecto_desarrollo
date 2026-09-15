import base64
import binascii
from typing import List
from fastapi import APIRouter, HTTPException, Request, status, UploadFile, File
from bson.errors import InvalidId
from app.core.database import database
from app.core.config import settings
from app.schemas.document_schema import DocumentResponse, DocumentUpdate, DocumentBase64Upload
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService

# Definicion del router con su prefijo y etiquetas para Swagger
router = APIRouter(prefix="/documents", tags=["documents"])


def get_client_ip(request: Request) -> str:
    """
    Obtiene la IP real del cliente.

    Si el pedido llega a través de un proxy o gateway (como Traefik), la IP
    original del cliente viaja en el header X-Forwarded-For (Traefik la
    agrega automáticamente). Si no hay proxy de por medio (por ejemplo,
    corriendo local sin Docker), usamos la IP de la conexión directa.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # El header puede traer una cadena de IPs si hubo varios proxies
        # ("cliente, proxy1, proxy2"); la primera es la del cliente real.
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _validar_extension(filename: str) -> None:
    """Valida que el nombre de archivo tenga una extensión permitida."""
    extension = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La extension del archivo debe ser: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )


def _validar_contenido_pdf(file_content: bytes) -> None:
    """
    Valida el contenido binario de un archivo ya leído: tamaño máximo y
    que sea realmente un PDF (magic bytes). Se usa tanto para la subida
    por multipart/form-data como para la subida por Base64, así ninguna
    de las dos rutas se salta estas validaciones.
    """
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo supera el limite permitido de 15MB"
        )

    if not file_content.startswith(b'%PDF'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El contenido del archivo no es un PDF valido"
        )


async def _procesar_y_guardar(file_content: bytes, filename: str, client_ip: str) -> DocumentResponse:
    """
    Punto único donde se arma el repositorio/servicio y se persiste el
    documento, ya validado. Ambos endpoints de subida (multipart y
    Base64) terminan llamando acá para no duplicar esta parte.
    """
    repo = DocumentRepository(database)
    service = DocumentService(repo)

    try:
        return await service.process_pdf(file_content, filename, client_ip)
    except ValueError as e:
        # Captura errores de duplicados (checksum) o errores de proceso
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Internal Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar el documento"
        )


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(request: Request, file: UploadFile = File(...)):
    """
    Endpoint para subir un PDF como archivo (multipart/form-data),
    extraer texto y persistirlo. Incluye validaciones de formato,
    tamano y contenido.
    """
    _validar_extension(file.filename)

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tipo de archivo debe ser application/pdf"
        )

    # Leer contenido en memoria (Requisito: Sin persistencia temporal)
    file_content = await file.read()
    _validar_contenido_pdf(file_content)

    client_ip = get_client_ip(request)
    return await _procesar_y_guardar(file_content, file.filename, client_ip)


@router.post("/upload-base64", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document_base64(request: Request, payload: DocumentBase64Upload):
    """
    Endpoint alternativo para subir un PDF codificado en Base64 dentro
    de un JSON, en vez de como archivo multipart. Útil para integraciones
    donde el cliente ya maneja el archivo como texto (por ejemplo, otro
    microservicio que reenvía el contenido en un payload JSON).

    Aplica exactamente las mismas validaciones y el mismo procesamiento
    que /upload: extensión, tamaño, magic bytes, checksum y extracción
    de texto.
    """
    _validar_extension(payload.filename)

    try:
        file_content = base64.b64decode(payload.file_base64, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El contenido Base64 es invalido o esta corrupto"
        )

    _validar_contenido_pdf(file_content)

    client_ip = get_client_ip(request)
    return await _procesar_y_guardar(file_content, payload.filename, client_ip)


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
