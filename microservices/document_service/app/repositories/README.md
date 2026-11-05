# Repositories Module

Capa de acceso a datos (Repository Pattern).

## Descripción
Gestiona todas las operaciones de persistencia de datos. Separa la lógica de acceso a la base de datos del resto de la aplicación.

## Principio SOLID
**Repository Pattern** - Encapsula el acceso a datos siguiendo el principio de responsabilidad única.

## Archivos

### user_repository.py
Métodos disponibles:

| Método | Descripción |
|--------|-------------|
| `get_by_id(id)` | Obtiene usuario por ID |
| `get_by_email(email)` | Obtiene usuario por email |
| `get_by_username(username)` | Obtiene usuario por username |
| `get_all(skip, limit)` | Lista todos los usuarios |
| `create(user)` | Crea nuevo usuario |
| `update(user)` | Actualiza usuario existente |
| `delete(user)` | Elimina usuario |
| `exists(id)` | Verifica si existe |

## Estructura
```python
class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        ...
```

## Requerimientos
```txt
sqlalchemy>=2.0.0
```

## Uso
```python
from app.repositories import UserRepository

def get_users(db: Session):
    repo = UserRepository(db)
    return repo.get_all()
```
