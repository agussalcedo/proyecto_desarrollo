Integrantes del grupo
Agustin Salcedo, Juan Pablo Cañada, Nicolas Martínez, Carlos Reta, Santiago Miscovich
Arquitectura
El sistema está compuesto por 3 piezas, todas levantadas con Docker Compose:
Traefik (puerto 80): gateway único de entrada. Enruta el tráfico hacia la API y aplica rate limiting por IP (bloquea con `429 Too Many Requests` a quien mande demasiados pedidos por segundo).
API (FastAPI): la lógica de negocio (documentos, orquestador).
MongoDB (puerto 27017): base de datos.
Todo el tráfico externo debe entrar por Traefik (`http://localhost`, sin `:8000`). La API no expone su puerto directamente hacia afuera.
Instalación y Ejecución
1. Requisitos Previos
Docker Desktop instalado y corriendo.
(Opcional, solo si querés correr la app sin Docker para desarrollo) uv y Python 3.12+.
k6 para correr las pruebas de carga.
2. Levantar todo el stack (Traefik + API + MongoDB)
```bash
git clone https://github.com/agussalcedo/proyecto_desarrollo.git
cd proyecto_desarrollo
docker-compose up --build -d
```
Verificar que los 3 contenedores estén arriba:
```bash
docker ps
```
Deberías ver `traefik_gateway`, `orchestrator_service` y `proyecto_desarrollo_db`.
3. Probar que funciona
```bash
curl http://localhost/health
```
Debería responder `{"status":"healthy"}`. La documentación interactiva de la API está en `http://localhost/docs`, y el dashboard de Traefik en `http://localhost:8080`.
4. Correr las pruebas de carga con k6
```bash
k6 run k6-tests/health_test.js
```
Esto simula una rampa de carga (10 → 33 → 50 usuarios virtuales concurrentes) contra `http://localhost/health`, pasando por Traefik. Resultados esperados:
Con tráfico moderado: mayoría de respuestas `200 OK`.
Al superar el límite configurado en Traefik (10 peticiones/seg promedio por IP): empiezan a aparecer respuestas `429 Too Many Requests`, lo cual confirma que el rate limiting está funcionando.
Los thresholds configurados en el script marcan la prueba como fallida si el percentil 95 de tiempo de respuesta supera 1 segundo, o si más del 10% de los pedidos falla.
5. Desarrollo local sin Docker (opcional)
Para trabajar en la API sin reconstruir el contenedor en cada cambio:
```bash
uv sync
docker-compose up -d mongo   # solo la base, no todo el stack
uv run uvicorn app.main:app --reload
uv run pytest -v             # correr los tests (no necesita Mongo corriendo)
```
En este modo la API queda en `http://localhost:8000` directo (sin pasar por Traefik), útil solo para desarrollo rápido.
