# Routes Module

Capa de presentación (Presentation Layer / Controllers).

## Descripción
Define los endpoints de la API usando FastAPI Router. Gestiona requests y responses HTTP.

## Principio SOLID
- **Controller Pattern**: Solo maneja HTTP
- **Dependency Injection**: Recibe servicios

## Archivos

### user_routes.py
Endpoints disponibles:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/users/` | Lista todos los usuarios |
| GET | `/users/{id}` | Obtiene usuario por ID |
| POST | `/users/` | Crea nuevo usuario |
| PATCH | `/users/{id}` | Actualiza usuario |
| DELETE | `/users/{id}` | Elimina usuario |

## Estructura
```python
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    ...
```

## Códigos de Respuesta
| Código | Descripción |
|--------|-------------|
| 200 | OK |
| 201 | Creado |
| 204 | Sin contenido |
| 400 | Bad Request |
| 404 | No encontrado |

## Dependencias
```python
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)
```

## Requerimientos
```txt
fastapi>=0.109.0
```

## Uso
```python
from app.routes import user_router

app.include_router(user_router)
```
