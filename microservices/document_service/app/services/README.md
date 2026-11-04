# Services Module

Capa de lógica de negocio (Business Logic Layer).

## Descripción
Contiene toda la lógica de negocio de la aplicación. Actúa como intermediario entre los routes y los repositories.

## Principio SOLID
- **Single Responsibility**: Solo maneja lógica de negocio
- **Dependency Injection**: Recibe repositories por constructor

## Archivos

### user_service.py
Servicios disponibles:

| Método | Descripción |
|--------|-------------|
| `get_user(id)` | Obtiene usuario por ID |
| `get_user_by_email(email)` | Obtiene usuario por email |
| `get_all_users(skip, limit)` | Lista usuarios |
| `create_user(data)` | Crea usuario con validaciones |
| `update_user(id, data)` | Actualiza usuario |
| `delete_user(id)` | Elimina usuario |
| `authenticate(email, password)` | Autentica usuario |

## Validaciones Incluidas
- Verificar email único
- Verificar username único
- Hash de contraseñas con bcrypt

## Estructura
```python
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def create_user(self, user_data: UserCreate) -> User:
        # Lógica de negocio
        ...
```

## Requerimientos
```txt
passlib[bcrypt]>=1.7.0
```

## Uso
```python
from app.services import UserService

def create_user_controller(user_data: UserCreate, db: Session):
    repository = UserRepository(db)
    service = UserService(repository)
    return service.create_user(user_data)
```
