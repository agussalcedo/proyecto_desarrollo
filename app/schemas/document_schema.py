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
    created_at: Optional[datetime] = None 

    class Config:
        from_attributes = True
        extra = "ignore" 

class DocumentUpdate(BaseModel):
    content: Optional[str] = None