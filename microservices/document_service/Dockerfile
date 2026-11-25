FROM python:3.12-slim

WORKDIR /app

# Usuario sin privilegios para correr la aplicación
RUN useradd --create-home appuser

# Copiamos las dependencias e instalamos
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código del proyecto
COPY --chown=appuser:appuser . .

# Exponemos el puerto de FastAPI
EXPOSE 8000

# A partir de acá se corre como usuario no root
USER appuser

# Comando para arrancar la API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]