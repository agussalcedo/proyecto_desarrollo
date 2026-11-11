from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class DocumentBase(BaseModel):
    filename: str
    content: str = Field(..., description="Texto extraído del PDF")
    checksum: str = Field(..., description="Suma de verificación del archivo")

class DocumentResponse(DocumentBase):
    id: str = Field(..., description="ID de MongoDB")
    size_bytes: int
    client_ip: Optional[str] = Field(None, description="IP del cliente que subió el documento")
    created_at: Optional[datetime] = None 

    class Config:
        from_attributes = True
        extra = "ignore" 

class DocumentUpdate(BaseModel):
    content: Optional[str] = None

class DocumentBase64Upload(BaseModel):
    """Payload para subir un PDF codificado en Base64 en vez de multipart/form-data."""
    filename: str = Field(..., description="Nombre del archivo, ej: parcial.pdf")
    file_base64: str = Field(..., description="Contenido del PDF codificado en Base64")