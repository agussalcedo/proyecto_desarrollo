"""
Aplicación FastAPI - Orchestrator Service
"""
from fastapi import FastAPI
from orchestrator_service.core.config import settings
from orchestrator_service.routes.orchestrator_routes import router as orchestrator_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Microservicio orquestador: coordina llamadas a otros microservicios.",
    version=settings.APP_VERSION,
)

app.include_router(orchestrator_router)


@app.get("/", tags=["Estado del Sistema"])
def root():
    """Endpoint de información general del microservicio."""
    return {"service": settings.APP_NAME, "version": settings.APP_VERSION, "status": "online"}


@app.get("/health", tags=["Estado del Sistema"])
def health_check():
    """Verificación básica de estado del servicio."""
    return {"status": "healthy"}