"""
Rutas HTTP - Health checks (Presentation Layer)
"""
from fastapi import APIRouter, Response, status

from orchestrator_service.schemas.orchestrator_schema import LivenessResponse, ReadinessResponse
from orchestrator_service.services.health_service import HealthService

# Detrás de Traefik este servicio se publica bajo /orchestrator, por eso el
# health vive en /orchestrator/health/... (alcanzable desde afuera y desde Docker).
router = APIRouter(prefix="/orchestrator/health", tags=["Estado del Sistema"])
_service = HealthService()


@router.get("/live", response_model=LivenessResponse)
def liveness():
    """Liveness: el proceso está vivo. No consulta dependencias."""
    return _service.liveness()


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={503: {"model": ReadinessResponse, "description": "Una dependencia no está lista"}},
)
async def readiness(response: Response):
    """Readiness: verifica el document_service y responde 503 si no está listo."""
    report = await _service.readiness()
    if report.status != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return report
