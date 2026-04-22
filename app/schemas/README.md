# Schemas Module

Data Transfer Objects (DTOs) para validación y serialización.

## Descripción
Contiene los schemas de Pydantic usados para:
- Validar datos de entrada
- Serializar datos de salida
- Documentación automática de API

## Archivos

### user_schema.py
Schemas para el modelo User:

| Schema         |                 Uso                      |
|----------------|------------------------------------------|
| `UserBase`     | Campos comunes (username, email)         |
| `UserCreate`   | Crear usuario (username, email, password)|
| `UserUpdate`   | Actualizar usuario (campos opcionales)   |
| `UserResponse` | Respuesta completa del usuario           |

## Ejemplos de Uso

### Crear Usuario
```python
from app.schemas import UserCreate

user_data = UserCreate(
    username="Agustin",
    email="agustin@gmail.com",
    password="123456"
)
```

### Respuesta
```python
from app.schemas import UserResponse

@router.get("/{id}", response_model=UserResponse)
def get_user(id: int):
    ...
```

## Requerimientos
```txt
pydantic>=2.0.0
email-validator>=2.0.0
```

## Uso
```python
from app.schemas import UserCreate, UserUpdate, UserResponse
```
