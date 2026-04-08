# Models Module

Capa de acceso a datos (Data Access Layer).

## Descripción
Contiene los modelos de SQLAlchemy que representan las entidades de la base de datos.

## Archivos

### user_model.py
Modelo User con los siguientes campos:
- `id`: Primary Key
- `username`: Unique, indexed
- `email`: Unique, indexed
- `hashed_password`: Contraseña encriptada
- `is_active`: Estado del usuario
- `created_at`: Timestamp de creación
- `updated_at`: Timestamp de actualización

## Estructura del Modelo
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

## Requerimientos
```txt
sqlalchemy>=2.0.0
```

## Uso
```python
from app.models import User
```
