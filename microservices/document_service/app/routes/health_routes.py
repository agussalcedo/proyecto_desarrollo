"""
Rutas HTTP - Health checks (Presentation Layer)
"""
from fastapi import APIRouter, Response, status

from app.schemas.health_schema import LivenessResponse, ReadinessResponse
from app.services.health_service import HealthService

router = APIRouter(tags=["Estado del Sistema"])
_service = HealthService()


@router.get("/health/live", response_model=LivenessResponse)
def liveness():
    """Liveness: el proceso está vivo. No consulta dependencias."""
    return _service.liveness()


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    responses={503: {"model": ReadinessResponse, "description": "Una dependencia no responde"}},
)
@router.get("/health", response_model=ReadinessResponse, include_in_schema=False)
async def readiness(response: Response):
    """
    Readiness: el servicio puede atender pedidos. Verifica MongoDB y responde
    503 si no está disponible. `/health` se mantiene como alias de este endpoint.
    """
    report = await _service.readiness()
    if report.status != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return report
