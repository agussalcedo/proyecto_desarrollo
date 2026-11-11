FROM python:3.12-slim

WORKDIR /app

# Copiamos las dependencias e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código del proyecto
COPY . .

# Exponemos el puerto de FastAPI
EXPOSE 8000

# Comando para arrancar la API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]