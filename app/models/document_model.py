"""
Data models - Data Access Layer (MongoDB/Pydantic Edition)
"""
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone
from typing import Optional

# Definimos la zona horaria de Argentina (GMT-3)
ARG_TZ = timezone(timedelta(hours=-3))

class Document(BaseModel):
    """
    Modelo de Documento para el procesamiento de PDFs.
    Cumple con el requerimiento de persistir contenido y checksum.
    """
    filename: str = Field(..., description="Nombre original del archivo")
    content: str = Field(..., description="Texto extraído del PDF")
    checksum: str = Field(..., description="Suma de verificación del archivo")
    size_bytes: int = Field(..., description="Tamaño del archivo validado")
    
    # Usamos default_factory para que se genere la hora exacta al momento de crear el objeto
    created_at: datetime = Field(default_factory=lambda: datetime.now(ARG_TZ)) 

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "parcial1.pdf",
                "content": "Contenido del examen...",
                "checksum": "a1b2c3d4...",
                "size_bytes": 5000,
                "created_at": "2026-04-21T21:05:00"
            }
        }
    }