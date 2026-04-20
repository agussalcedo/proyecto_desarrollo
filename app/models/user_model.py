"""
Data models - Data Access Layer (MongoDB/Pydantic Edition)
"""
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    """
    Modelo de Usuario siguiendo el principio KISS (Mantenerlo Simple).
    Usamos Pydantic para validar los datos antes de que lleguen a la DB.
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # Principio SOLID (O): El modelo es extensible mediante configuraciones
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "aguss_dev",
                "email": "aguss@example.com",
                "hashed_password": "password_seguro_123",
                "is_active": True
            }
        }
    }