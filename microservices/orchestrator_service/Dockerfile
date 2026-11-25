FROM python:3.12-slim

WORKDIR /app

# Usuario sin privilegios para correr la aplicación
RUN useradd --create-home appuser

# Copiamos las dependencias e instalamos
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código del microservicio
COPY --chown=appuser:appuser . .

# Exponemos el puerto de FastAPI
EXPOSE 8000

# A partir de acá se corre como usuario no root
USER appuser

# Comando para arrancar el orquestador
CMD ["uvicorn", "orchestrator_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
