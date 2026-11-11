# Models Module

Capa de acceso a datos (Data Access Layer).

# Descripción

Contiene los modelos de Pydantic que representan los esquemas de los documentos en MongoDB. A diferencia de los modelos relacionales, aquí se definen estructuras flexibles con validación automática de tipos.

# Archivos

document_model.py

filename: Nombre original del archivo.
content: Texto extraído del PDF.
checksum: Suma de verificación (Hash) para integridad de datos.
size_bytes: Tamaño del archivo validado.
created_at: Timestamp de creación con zona horaria de Argentina (GMT-3).

# Estructura del modelo
```bash
class Document(BaseModel):
    filename: str
    content: str
    checksum: str
    size_bytes: int
    created_at: datetime
```
# Requerimentos

pydantic >=2.10.0

# Uso
```bash
from app.models import Document
```
