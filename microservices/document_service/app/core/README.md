# Core Module

Configuración central de la aplicación.

## Archivos

### config.py
Configuraciones de la aplicación usando Pydantic Settings.
- Variables de entorno
- Configuración de base de datos
- Parámetros de la aplicación

### database.py
Gestión de conexiones a la base de datos.
- Motor MONGODB

## Requerimientos

``` pydantic-settings>=2.0.0 ``` 

## Uso
```python
from app.core.database import get_db, engine, Base
from app.core.config import settings
```