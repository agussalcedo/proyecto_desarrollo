"""
Aplicación FastAPI - Orchestrator Service
"""
from fastapi import FastAPI
from orchestrator_service.core.config import settings
from orchestrator_service.routes.health_routes import router as health_router
from orchestrator_service.routes.orchestrator_routes import router as orchestrator_router

# Detrás de Traefik este servicio se publica bajo /orchestrator, por eso su
# documentación vive en /orchestrator/docs (en /docs responde el document_service).
app = FastAPI(
    title=settings.APP_NAME,
    description="Microservicio orquestador: coordina llamadas a otros microservicios.",
    version=settings.APP_VERSION,
    docs_url="/orchestrator/docs",
    openapi_url="/orchestrator/openapi.json",
)

app.include_router(orchestrator_router)
app.include_router(health_router)


@app.get("/", tags=["Estado del Sistema"])
def root():
    """Endpoint de información general del microservicio."""
    return {"service": settings.APP_NAME, "version": settings.APP_VERSION, "status": "online"}
